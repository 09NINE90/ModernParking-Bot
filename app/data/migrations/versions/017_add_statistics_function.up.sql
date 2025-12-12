CREATE OR REPLACE FUNCTION DEFAULT_SCHEMA.get_parking_stats_by_period(
    p_period_type VARCHAR DEFAULT 'week',
    p_period_count INTEGER DEFAULT NULL
)
RETURNS TABLE (
    period_display TEXT,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    total_requests BIGINT,
    accepted_requests BIGINT,
    pending_requests BIGINT,
    canceled_requests BIGINT,
    not_found_requests BIGINT,
    waiting_confirmation_requests BIGINT,
    total_releases BIGINT,
    accepted_releases BIGINT,
    pending_releases BIGINT,
    canceled_releases BIGINT,
    not_found_releases BIGINT,
    waiting_releases BIGINT,
    unique_requesters BIGINT,
    unique_releasers BIGINT,
    unique_recipients BIGINT,
    unique_spots_released BIGINT,
    request_success_rate NUMERIC,
    release_success_rate NUMERIC,
    market_balance TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    start_date TIMESTAMP;
    interval_step INTERVAL;
    default_period_count INTEGER;
BEGIN
    -- Определяем количество периодов и шаг интервала в зависимости от типа периода
    CASE p_period_type
        WHEN 'day' THEN
            default_period_count := 30;
            start_date := CURRENT_DATE - INTERVAL '30 days';
            interval_step := INTERVAL '1 day';
        WHEN 'week' THEN
            default_period_count := 12;
            start_date := CURRENT_DATE - INTERVAL '12 weeks';
            interval_step := INTERVAL '1 week';
        WHEN 'month' THEN
            default_period_count := 6;
            start_date := CURRENT_DATE - INTERVAL '6 months';
            interval_step := INTERVAL '1 month';
        WHEN 'quarter' THEN
            default_period_count := 4;
            start_date := CURRENT_DATE - INTERVAL '1 year'; -- 4 квартала
            interval_step := INTERVAL '3 months';
        WHEN 'year' THEN
            default_period_count := 3;
            start_date := CURRENT_DATE - INTERVAL '3 years';
            interval_step := INTERVAL '1 year';
        ELSE
            RAISE EXCEPTION 'Неверный тип периода. Используйте: day, week, month, quarter, year';
    END CASE;

    IF p_period_count IS NULL THEN
        p_period_count := default_period_count;
    END IF;

    -- Проверяем, что количество периодов положительное
    IF p_period_count <= 0 THEN
        RAISE EXCEPTION 'Количество периодов должно быть положительным числом. Получено: %', p_period_count;
    END IF;

    CASE p_period_type
        WHEN 'day' THEN
            start_date := CURRENT_DATE - (p_period_count || ' days')::INTERVAL;
        WHEN 'week' THEN
            start_date := CURRENT_DATE - (p_period_count || ' weeks')::INTERVAL;
        WHEN 'month' THEN
            start_date := CURRENT_DATE - (p_period_count || ' months')::INTERVAL;
        WHEN 'quarter' THEN
            start_date := CURRENT_DATE - (p_period_count * 3 || ' months')::INTERVAL;
        WHEN 'year' THEN
            start_date := CURRENT_DATE - (p_period_count || ' years')::INTERVAL;
    END CASE;

    RETURN QUERY
    WITH periods AS (
        SELECT
            -- Определяем начало периода
            CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', d.date)
                WHEN 'week' THEN DATE_TRUNC('week', d.date)
                WHEN 'month' THEN DATE_TRUNC('month', d.date)
                WHEN 'quarter' THEN DATE_TRUNC('quarter', d.date)
                WHEN 'year' THEN DATE_TRUNC('year', d.date)
            END as period_start,

            -- Определяем конец периода
            CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', d.date) + INTERVAL '1 day' - INTERVAL '1 second'
                WHEN 'week' THEN DATE_TRUNC('week', d.date) + INTERVAL '1 week' - INTERVAL '1 second'
                WHEN 'month' THEN DATE_TRUNC('month', d.date) + INTERVAL '1 month' - INTERVAL '1 second'
                WHEN 'quarter' THEN DATE_TRUNC('quarter', d.date) + INTERVAL '3 months' - INTERVAL '1 second'
                WHEN 'year' THEN DATE_TRUNC('year', d.date) + INTERVAL '1 year' - INTERVAL '1 second'
            END as period_end,

            -- Форматируем отображение периода
            CASE p_period_type
                WHEN 'day' THEN TO_CHAR(d.date, 'DD.MM.YYYY')
                WHEN 'week' THEN TO_CHAR(DATE_TRUNC('week', d.date), 'DD.MM') || ' - ' ||
                               TO_CHAR(DATE_TRUNC('week', d.date) + INTERVAL '6 days', 'DD.MM.YYYY')
                WHEN 'month' THEN TO_CHAR(d.date, 'Month YYYY')
                WHEN 'quarter' THEN EXTRACT(QUARTER FROM d.date) || 'Q' || EXTRACT(YEAR FROM d.date)
                WHEN 'year' THEN TO_CHAR(d.date, 'YYYY')
            END as period_display

        FROM generate_series(start_date, CURRENT_DATE, interval_step) d(date)
    )
    SELECT
        p.period_display::TEXT,
        p.period_start::TIMESTAMP,
        p.period_end::TIMESTAMP,

        -- Статистика запросов
        COALESCE(req.total_requests, 0)::BIGINT,
        COALESCE(req.accepted_requests, 0)::BIGINT,
        COALESCE(req.pending_requests, 0)::BIGINT,
        COALESCE(req.canceled_requests, 0)::BIGINT,
        COALESCE(req.not_found_requests, 0)::BIGINT,
        COALESCE(req.waiting_confirmation_requests, 0)::BIGINT,

        -- Статистика освобождений
        COALESCE(rel.total_releases, 0)::BIGINT,
        COALESCE(rel.accepted_releases, 0)::BIGINT,
        COALESCE(rel.pending_releases, 0)::BIGINT,
        COALESCE(rel.canceled_releases, 0)::BIGINT,
        COALESCE(rel.not_found_releases, 0)::BIGINT,
        COALESCE(rel.waiting_releases, 0)::BIGINT,

        -- Уникальные пользователи
        COALESCE(req.unique_requesters, 0)::BIGINT,
        COALESCE(rel.unique_releasers, 0)::BIGINT,
        COALESCE(rel.unique_recipients, 0)::BIGINT,
        COALESCE(rel.unique_spots_released, 0)::BIGINT,

        -- Расчетные показатели
        ROUND(
            COALESCE(req.accepted_requests, 0) * 100.0 /
            NULLIF(COALESCE(req.total_requests, 0), 0), 1
        )::NUMERIC,

        ROUND(
            COALESCE(rel.accepted_releases, 0) * 100.0 /
            NULLIF(COALESCE(rel.total_releases, 0), 0), 1
        )::NUMERIC,

        -- Баланс спроса и предложения
        CASE
            WHEN COALESCE(req.total_requests, 0) > COALESCE(rel.total_releases, 0)
            THEN 'Дефицит мест: ' || (COALESCE(req.total_requests, 0) - COALESCE(rel.total_releases, 0))::TEXT
            WHEN COALESCE(req.total_requests, 0) < COALESCE(rel.total_releases, 0)
            THEN 'Избыток мест: ' || (COALESCE(rel.total_releases, 0) - COALESCE(req.total_requests, 0))::TEXT
            ELSE 'Баланс'
        END::TEXT

    FROM periods p

    -- Статистика запросов
    LEFT JOIN (
        SELECT
            CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', request_date)
                WHEN 'week' THEN DATE_TRUNC('week', request_date)
                WHEN 'month' THEN DATE_TRUNC('month', request_date)
                WHEN 'quarter' THEN DATE_TRUNC('quarter', request_date)
                WHEN 'year' THEN DATE_TRUNC('year', request_date)
            END as period_start,
            COUNT(*) as total_requests,
            COUNT(CASE WHEN status = 'ACCEPTED' THEN 1 END) as accepted_requests,
            COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_requests,
            COUNT(CASE WHEN status = 'CANCELED' THEN 1 END) as canceled_requests,
            COUNT(CASE WHEN status = 'NOT_FOUND' THEN 1 END) as not_found_requests,
            COUNT(CASE WHEN status = 'WAITING_CONFIRMATION' THEN 1 END) as waiting_confirmation_requests,
            COUNT(DISTINCT user_id) as unique_requesters
        FROM DEFAULT_SCHEMA.parking_requests
        WHERE request_date >= start_date
        GROUP BY CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', request_date)
                WHEN 'week' THEN DATE_TRUNC('week', request_date)
                WHEN 'month' THEN DATE_TRUNC('month', request_date)
                WHEN 'quarter' THEN DATE_TRUNC('quarter', request_date)
                WHEN 'year' THEN DATE_TRUNC('year', request_date)
            END
    ) req ON p.period_start = req.period_start

    -- Статистика освобождений
    LEFT JOIN (
        SELECT
            CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', release_date)
                WHEN 'week' THEN DATE_TRUNC('week', release_date)
                WHEN 'month' THEN DATE_TRUNC('month', release_date)
                WHEN 'quarter' THEN DATE_TRUNC('quarter', release_date)
                WHEN 'year' THEN DATE_TRUNC('year', release_date)
            END as period_start,
            COUNT(*) as total_releases,
            COUNT(CASE WHEN status = 'ACCEPTED' THEN 1 END) as accepted_releases,
            COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_releases,
            COUNT(CASE WHEN status = 'CANCELED' THEN 1 END) as canceled_releases,
            COUNT(CASE WHEN status = 'NOT_FOUND' THEN 1 END) as not_found_releases,
            COUNT(CASE WHEN status = 'WAITING' THEN 1 END) as waiting_releases,
            COUNT(DISTINCT user_id) as unique_releasers,
            COUNT(DISTINCT user_id_took) as unique_recipients,
            COUNT(DISTINCT spot_id) as unique_spots_released
        FROM DEFAULT_SCHEMA.parking_releases
        WHERE release_date >= start_date
        GROUP BY CASE p_period_type
                WHEN 'day' THEN DATE_TRUNC('day', release_date)
                WHEN 'week' THEN DATE_TRUNC('week', release_date)
                WHEN 'month' THEN DATE_TRUNC('month', release_date)
                WHEN 'quarter' THEN DATE_TRUNC('quarter', release_date)
                WHEN 'year' THEN DATE_TRUNC('year', release_date)
            END
    ) rel ON p.period_start = rel.period_start

    ORDER BY p.period_start DESC;
END;
$$;