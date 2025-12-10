class CallbackData:
    # Базовые
    BACK_TO_MAIN = "back_to_main"
    MY_STATISTICS = "my_statistics"

    # Места
    RELEASE_SPOT = "release_spot"
    REVOKE_RELEASE = "revoke_release"
    REQUEST_SPOT = "request_spot"
    REVOKE_REQUEST = "revoke_request"
    TAKE_SPOT = "take_spot"
    CANCEL_SPOT = "cancel_spot"
    TAKE_SPOT_BY_REMINDER = "take_spot_by_reminder"
    CANCEL_SPOT_BY_REMINDER = "cancel_spot_by_reminder"

    # Расписания
    CREATE_DEFAULT_SCHEDULE = "create_default_schedule"
    DELETE_DEFAULT_SCHEDULE = "delete_default_schedule"
    SAVE_SCHEDULE = "save_schedule"
    ADD_DAY_PREFIX = "add_day_"
    DEL_PREFIX = "del_"
    YES_DEL_PREFIX = "yes_del_"
    SELECT_PREFIX = "select_"
    CANCEL_SCHEDULE_SELECTION = "cancel_schedule_selection"

    # Обратная связь
    FEEDBACK_PREFIX = "feedback_"
    FEEDBACK_ERROR = "feedback_error"
    FEEDBACK_IDEA = "feedback_idea"
    FEEDBACK_FEEDBACK = "feedback_feedback"

    # Префиксы для callback данных
    RELEASE_DATE_PREFIX = "release_date_"
    REQUEST_DATE_PREFIX = "request_date_"
    CONFIRMATION_REVOKE_RELEASE_PREFIX = "confirmation_revoke_release_"
    CONFIRM_REVOKE_RELEASE_PREFIX = "confirm_revoke_release_"
    CONFIRMATION_REVOKE_REQUEST_PREFIX = "confirmation_revoke_request_"
    CONFIRM_REVOKE_REQUEST_PREFIX = "confirm_revoke_request_"

    # Админ
    MAIN_ADMIN = "main_admin"
    ALL_STATISTICS = "all_statistics"