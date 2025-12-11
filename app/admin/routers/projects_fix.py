# ИСПРАВЛЕНИЕ ДЛЯ ФУНКЦИИ get_projects
# Заменяем синхронную версию на асинхронную

from sqlalchemy import select, or_, desc, asc, func
from sqlalchemy.orm import joinedload

async def get_projects_fixed(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_desc",
    show_archived: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Получить список проектов с фильтрами (с учетом ролей доступа)"""
    try:
        logger.info(f"[API] GET /api/projects/ - Пользователь: {current_user['username']}, Роль: {current_user['role']}, ID: {current_user['id']}")

        async with get_db_context() as db:
            # Начинаем с базового запроса
            stmt = select(Project).options(
                joinedload(Project.user)  # Предзагрузка пользователя
            )

            # Фильтр архивных проектов
            if show_archived:
                stmt = stmt.filter(Project.is_archived == True)
            else:
                stmt = stmt.filter(or_(Project.is_archived == False, Project.is_archived == None))

            # Фильтрация по роли пользователя
            if current_user["role"] == "executor":
                # Исполнитель видит только назначенные ему проекты
                logger.info(f"[API] Фильтрация для исполнителя: assigned_executor_id == {current_user['id']}")
                stmt = stmt.filter(Project.assigned_executor_id == current_user["id"])
            else:
                logger.info(f"[API] Роль {current_user['role']} - показываем все проекты")
            # Владелец видит все проекты (без дополнительных фильтров)

            # Применяем остальные фильтры
            if status:
                stmt = stmt.filter(Project.status == status)

            if priority:
                stmt = stmt.filter(Project.priority == priority)

            if search:
                # Добавляем join для поиска по имени пользователя
                stmt = stmt.join(User, Project.user_id == User.id, isouter=True)
                search_filter = or_(
                    Project.title.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%")
                )
                stmt = stmt.filter(search_filter)

            # Применяем сортировку
            if sort_by == "created_desc":
                stmt = stmt.order_by(desc(Project.created_at))
            elif sort_by == "created_asc":
                stmt = stmt.order_by(asc(Project.created_at))
            else:
                stmt = stmt.order_by(desc(Project.updated_at))

            # Подсчитываем общее количество
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await db.execute(count_stmt)
            total = total_result.scalar()
            logger.info(f"[API] После фильтрации найдено проектов: {total}")

            # Применяем пагинацию
            offset = (page - 1) * per_page
            stmt = stmt.offset(offset).limit(per_page)

            # Выполняем запрос
            result = await db.execute(stmt)
            projects = result.scalars().all()
            logger.info(f"[API] Возвращаем проектов на странице: {len(projects)}")

            # Конвертируем в словари с дополнительной информацией
            projects_data = []
            for project in projects:
                project_dict = project.to_dict()

                # Информация о пользователе уже загружена через joinedload
                if project.user:
                    user_dict = project.user.to_dict()

                    # Добавляем Telegram ID из preferences или metadata проекта
                    telegram_id = ""
                    if project.user.preferences and project.user.preferences.get('telegram_id'):
                        telegram_id = project.user.preferences.get('telegram_id', '')
                    elif project.project_metadata and project.project_metadata.get('user_telegram_id'):
                        telegram_id = project.project_metadata.get('user_telegram_id', '')

                    user_dict["telegram_id"] = telegram_id

                    # Для исполнителей скрываем username и контактные данные клиента
                    if current_user["role"] == "executor":
                        user_dict.pop("username", None)
                        user_dict.pop("phone", None)
                        user_dict.pop("email", None)
                        user_dict.pop("telegram_id", None)

                    project_dict["user"] = user_dict

                # Добавляем информацию об исполнителе
                if project.assigned_executor_id:
                    executor_stmt = select(AdminUser).filter(AdminUser.id == project.assigned_executor_id)
                    executor_result = await db.execute(executor_stmt)
                    executor = executor_result.scalar_one_or_none()

                    if executor:
                        executor_data = {
                            "id": executor.id,
                            "username": executor.username,
                            "first_name": executor.first_name,
                            "last_name": executor.last_name,
                            "role": executor.role
                        }
                        project_dict["executor"] = executor_data

                # Добавляем информацию о менеджере
                if project.responsible_manager_id:
                    manager_stmt = select(AdminUser).filter(AdminUser.id == project.responsible_manager_id)
                    manager_result = await db.execute(manager_stmt)
                    manager = manager_result.scalar_one_or_none()

                    if manager:
                        manager_data = {
                            "id": manager.id,
                            "username": manager.username,
                            "first_name": manager.first_name,
                            "last_name": manager.last_name
                        }
                        project_dict["responsible_manager"] = manager_data

                # Добавляем количество файлов
                files_stmt = select(func.count()).select_from(ProjectFile).filter(ProjectFile.project_id == project.id)
                files_result = await db.execute(files_stmt)
                project_dict["files_count"] = files_result.scalar()

                # Добавляем количество ревизий
                revisions_stmt = select(func.count()).select_from(ProjectRevision).filter(ProjectRevision.project_id == project.id)
                revisions_result = await db.execute(revisions_stmt)
                project_dict["revisions_count"] = revisions_result.scalar()

                projects_data.append(project_dict)

            response_data = {
                "projects": projects_data,
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }

            logger.info(f"[API] Возвращаем ответ с {len(projects_data)} проектами")
            return response_data

    except Exception as e:
        logger.error(f"[API] Ошибка при получении проектов: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка при получении проектов: {str(e)}")