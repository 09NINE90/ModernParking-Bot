from app.data.models import ScheduleDto
from app.repositories import SpotRequestsScheduleRepository


class SpotRequestsScheduleService:
    """Сервис для работы с расписаниями запросов"""

    def __init__(self, repository: SpotRequestsScheduleRepository):
        self.repository = repository

    def add_spot_requests_schedule(self, user_id, day_numbers):
        return self.repository.add_spot_requests_schedule(user_id, day_numbers)

    def get_spot_requests_schedule_by_user(self, user_id):
        return self.repository.get_spot_requests_schedule_by_user(user_id)

    def get_spot_requests_schedule_by_user_with_id(self, user_id):
        results = self.repository.get_spot_requests_schedule_by_user_with_id(user_id)
        if results:
            return [
                ScheduleDto(
                    id=row[0],
                    day_numbers=row[1]
                )
                for row in results
            ]
        return None

    def get_spot_requests_schedule_by_id(self, schedule_id):
        result = self.repository.get_spot_requests_schedule_by_id(schedule_id)
        if result:
            return ScheduleDto(
                id=result[0],
                day_numbers=result[1]
            )

        return None


    def delete_spot_requests_schedule_by_id(self, schedule_id):
        return self.repository.delete_spot_requests_schedule_by_id(schedule_id)


    def get_user_schedules_with_tg_id(self):
        results = self.repository.get_user_schedules_with_tg_id()

        result = {}
        if results:
            for row in results:
                tg_id = row[0]
                schedules_data = row[1]

                schedules = [ScheduleDto(id=sched['id'], day_numbers=sched['day_numbers'])
                             for sched in schedules_data]

                result[tg_id] = schedules

        return result
