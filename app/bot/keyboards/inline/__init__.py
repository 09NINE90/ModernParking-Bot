from .base import (
    back_to_main_markup,
    back_to_revoke_request_markup,
    back_to_revoke_release_markup,
    back_to_create_default_schedule_markup,
    back_to_delete_default_schedule_markup,
    feedback_markup,
    main_markup,
    found_spot_markup,
    reminder_spot_confirmation_markup,
    success_save_default_schedule_markup,
)

from .schedules import (
    create_default_schedule_markup,
    create_delete_schedules_keyboard,
    confirmation_delete_schedule_markup,
    schedule_selection_markup,
)

from .dates import (
    date_list_markup,
    revoke_releases_markup,
    revoke_requests_markup,
    confirmation_revoke_release_markup,
    confirmation_revoke_requests_markup,
)

from .admin import (
    main_admin_markup
)

__all__ = [
    # Base
    'back_to_main_markup',
    'back_to_revoke_request_markup',
    'back_to_revoke_release_markup',
    'back_to_create_default_schedule_markup',
    'back_to_delete_default_schedule_markup',
    'feedback_markup',
    'main_markup',
    'found_spot_markup',
    'reminder_spot_confirmation_markup',
    'success_save_default_schedule_markup',

    # Schedules
    'create_default_schedule_markup',
    'create_delete_schedules_keyboard',
    'confirmation_delete_schedule_markup',
    'schedule_selection_markup',

    # Dates
    'date_list_markup',
    'revoke_releases_markup',
    'revoke_requests_markup',
    'confirmation_revoke_requests_markup',
    'confirmation_revoke_release_markup',

    # Admin
    'main_admin_markup'
]
