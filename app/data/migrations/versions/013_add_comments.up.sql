COMMENT ON TABLE DEFAULT_SCHEMA.users IS 'Таблица пользователей Telegram-бота для парковки';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.user_id IS 'Внутренний UUID пользователя';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.tg_id IS 'Telegram ID пользователя';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.status IS 'Статус активации: true - активен, false - заблокирован';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.rating IS 'Рейтинг пользователя (количество успешно полученных парковочных мест)';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.created_at IS 'Дата и время регистрации пользователя в системе';
COMMENT ON COLUMN DEFAULT_SCHEMA.users.roles IS 'Роль пользователя: USER или ADMIN';

COMMENT ON TABLE DEFAULT_SCHEMA.parking_spots IS 'Таблица парковочных мест на парковке';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_spots.spot_id IS 'Уникальный номер парковочного места';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_spots.is_active IS 'Доступность места: true - доступно для бронирования, false - недоступно';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_spots.floor_number IS 'Номер этажа, на котором расположено парковочное место';

COMMENT ON TABLE DEFAULT_SCHEMA.parking_requests IS 'Таблица запросов на парковочные места. Хранит историю всех заявок пользователей.';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.id IS 'Уникальный идентификатор запроса (UUID)';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.user_id IS 'ID пользователя, создавшего запрос. Ссылается на users.user_id';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.request_date IS 'Дата, на которую запрашивается парковочное место (день парковки)';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.status IS 'Статус запроса: PENDING - ожидает обработки, ACCEPTED - подтвержден, CANCELED - отменен, NOT_FOUND - место не найдено, WAITING_CONFIRMATION - ожидает подтверждения пользователя';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.created_at IS 'Дата и время создания запроса в системе';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.processed_at IS 'Дата и время, изменения статуса';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_requests.is_auto_request IS 'Создание запроса с помощью расписания: true - да, false - нет';

COMMENT ON TABLE DEFAULT_SCHEMA.parking_releases IS 'Таблица освобождения парковочных мест';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.id IS 'Уникальный идентификатор записи об освобождении места (UUID)';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.user_id IS 'ID пользователя, который освобождает парковочное место (владелец места)';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.spot_id IS 'ID освобождаемого парковочного места. Ссылается на parking_spots.spot_id';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.release_date IS 'Дата, на которую освобождается парковочное место';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.created_at IS 'Дата и время создания записи об освобождении места';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.user_id_took IS 'ID пользователя, который занял освобожденное место (если уже передан). NULL если место еще свободно';
COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.status IS 'Статус освобождения: PENDING - ожидает распределения, ACCEPTED - место успешно передано, CANCELED - отмена передачи места, NOT_FOUND - место не отдано, WAITING - ожидает подтверждения получателя';

COMMENT ON TABLE DEFAULT_SCHEMA.reminder_spot_confirmations IS 'Таблица напоминаний о подтверждении парковочных мест';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.id IS 'Уникальный идентификатор напоминания (генерируется автоматически)';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.user_id IS 'ID пользователя, которому отправляется напоминание';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.release_id IS 'ID связанного освобождения места';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.request_id IS 'ID связанного запроса на место';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.created_at IS 'Дата и время создания записи о напоминании';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.updated_at IS 'Дата и время последнего обновления записи';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.is_active IS 'Флаг активности напоминания: true - напоминание активно, false - напоминание отработало';
COMMENT ON COLUMN DEFAULT_SCHEMA.reminder_spot_confirmations.message_sent_id IS 'Идентификатор отправленного сообщения в Telegram (для отслеживания и управления)';

COMMENT ON TABLE DEFAULT_SCHEMA.spot_confirmations IS 'Таблица подтверждений занятий парковочных мест';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.id IS 'Уникальный идентификатор подтверждения (генерируется автоматически)';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.user_id IS 'ID пользователя, которому предложено место';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.release_id IS 'ID связанного освобождения места';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.request_id IS 'ID связанного запроса на место';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.created_at IS 'Дата и время создания записи о подтверждении';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.updated_at IS 'Дата и время последнего обновления подтверждения';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.is_active IS 'Статус подтверждения: true - подтверждение актуально, false - подтверждение аннулировано или отозвано';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.message_sent_id IS 'ID сообщения в Telegram, связанного с этим подтверждением (для управления сообщениями)';

COMMENT ON TABLE DEFAULT_SCHEMA.spot_requests_schedule IS 'Таблица шаблонов расписаний для автоматического создания запросов на парковочные места. Пользователи настраивают дни недели для регулярных бронирований.';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_requests_schedule.id IS 'Уникальный идентификатор шаблона расписания (генерируется автоматически)';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_requests_schedule.user_id IS 'ID пользователя, которому принадлежит шаблон расписания';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_requests_schedule.day_numbers IS 'Номера дней недели для автоматических запросов в формате через запятую: 0-Понедельник, 1-Вторник, 2-Среда, 3-Четверг, 4-Пятница, 5-Суббота, 6-Воскресенье. Пример: "1,3,4" для вторника, четверга, пятницы';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_requests_schedule.created_at IS 'Дата и время создания шаблона расписания';





