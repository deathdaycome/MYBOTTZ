PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	telegram_id INTEGER NOT NULL, 
	username VARCHAR(255), 
	first_name VARCHAR(255), 
	last_name VARCHAR(255), 
	phone VARCHAR(20), 
	email VARCHAR(255), 
	registration_date DATETIME, 
	last_activity DATETIME, 
	state VARCHAR(100), 
	preferences JSON, 
	notes TEXT, 
	is_active BOOLEAN, bot_token VARCHAR(500), timeweb_login VARCHAR(255), timeweb_password VARCHAR(255), user_telegram_id VARCHAR(50), chat_id VARCHAR(50), bot_configured BOOLEAN DEFAULT FALSE, 
	PRIMARY KEY (id)
);
INSERT INTO users VALUES(1,501613334,'laytraces','Lay Traces',NULL,NULL,NULL,'2025-07-08 09:50:25.373461','2025-08-04 09:01:31.898387','main_menu','{"bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"}',NULL,1,NULL,NULL,NULL,'501613334',NULL,0);
INSERT INTO users VALUES(2,123456789,'testuser','Test','User',NULL,NULL,'2025-07-09 09:35:59.746500','2025-07-09 09:42:28.611510','main_menu','{"bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", "bot_token_added_at": "2025-07-16T10:30:00", "timeweb_credentials": {"login": "test@example.com", "password": "password123", "created_at": "2025-07-16T10:25:00"}}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(3,12345,'test_user','Тест',NULL,'+79123456789','test@example.com','2025-07-09 09:49:51.734705','2025-07-16 10:42:52.316823','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(4,55555,'test_api_user','Тест API',NULL,'+79123456789','test_api@example.com','2025-07-09 09:53:02.308440','2025-07-09 09:53:02.308445','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(5,392743569,'Marina_vSTART','Марина СТАРТ',NULL,NULL,NULL,'2025-07-16 12:47:53.429217','2025-07-16 12:47:53.433403','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(6,289644296,'Invnv','Natalya','Ivanisheva',NULL,NULL,'2025-07-16 15:47:24.381651','2025-07-16 15:56:00.333915','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(7,3,NULL,NULL,NULL,NULL,NULL,'2025-07-17 08:19:51.845109','2025-07-17 08:19:51.850501','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(8,123,'test_user','Test','User',NULL,NULL,'2025-07-17 08:23:25.397657','2025-07-17 08:23:25.398936','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(9,737068813,'lockinbaby','NNG',NULL,NULL,NULL,'2025-07-17 10:24:23.671590','2025-07-26 00:42:12.883113','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(10,'@truetechshop','','Yekemini','','-',NULL,'2025-07-19 10:38:34.940581','2025-07-19 10:38:34.940602','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(11,6898088562,'','акака','','',NULL,'2025-07-19 11:12:44.564761','2025-08-03 13:52:00.267426','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(12,5804228677,'truetechshop','True','Tech',NULL,NULL,'2025-07-20 13:47:11.244797','2025-07-20 13:47:11.249215','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(13,999842003,'Vitalii_001','Виталий',NULL,NULL,NULL,'2025-07-20 21:16:39.542087','2025-07-20 21:21:09.024241','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(14,6261590247,'ezgef','𓅻ࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩ 𓅻ࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩ',NULL,NULL,NULL,'2025-07-20 21:19:13.081317','2025-07-20 21:19:30.068562','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(15,8086446670,NULL,'ijkoup','jmcdaid',NULL,NULL,'2025-07-21 22:07:54.924267','2025-07-21 22:07:54.930149','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(16,5111697699,NULL,'Геннадий','Николаев',NULL,NULL,'2025-07-22 10:22:09.242383','2025-08-03 13:47:45.703082','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(17,469979893,'Zueva_Larisa','Larisa','Zueva',NULL,NULL,'2025-07-22 11:16:16.135108','2025-07-22 12:17:11.657158','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(18,5147523936,NULL,'CEO',NULL,NULL,NULL,'2025-07-22 11:20:04.270349','2025-07-22 11:20:31.832720','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(19,1221313,'','какакак','','',NULL,'2025-07-24 09:16:23.061319','2025-07-24 09:16:23.061324','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(20,323233332,'','какака','','332',NULL,'2025-07-26 09:32:26.664487','2025-07-26 09:32:26.664504','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(21,12345678,'','Виктор','','+79877510702',NULL,'2025-07-28 06:23:17.406303','2025-07-28 06:23:17.406308','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(22,344,'6576','6576',NULL,'',NULL,'2025-08-01 20:16:26.217329','2025-08-01 20:16:26.218515','registered','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(23,123314,'refrfref','refrfref',NULL,'frrfre',NULL,'2025-08-02 10:50:49.083226','2025-08-02 10:50:49.085230','registered','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(24,32233,'rfrff','rfrff',NULL,'+79877510702',NULL,'2025-08-02 10:51:47.990404','2025-08-02 10:51:47.990647','registered','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(25,7754133390,'WestWeek','West','Week',NULL,NULL,'2025-08-03 08:54:36.841990','2025-08-03 08:59:20.654444','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
CREATE TABLE portfolio (
	id INTEGER NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	subtitle VARCHAR(500), 
	description TEXT NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	main_image VARCHAR(500), 
	image_paths JSON, 
	technologies TEXT, 
	complexity VARCHAR(20), 
	complexity_level INTEGER, 
	development_time INTEGER, 
	cost FLOAT, 
	cost_range VARCHAR(100), 
	show_cost BOOLEAN, 
	demo_link VARCHAR(500), 
	repository_link VARCHAR(500), 
	external_links JSON, 
	is_featured BOOLEAN, 
	is_visible BOOLEAN, 
	sort_order INTEGER, 
	views_count INTEGER, 
	likes_count INTEGER, 
	tags TEXT, 
	client_name VARCHAR(200), 
	project_status VARCHAR(50), 
	completed_at DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	created_by INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO portfolio VALUES(1,'Бот для интернет-магазина',NULL,'Многофункциональный бот с каталогом товаров, корзиной, оплатой и уведомлениями о заказах','telegram_bot','telegram_bot_demo.jpg','[]','Python, Telegram Bot API, SQLite, Stripe API','medium',7,14,NULL,'35000-45000',0,NULL,NULL,'[]',1,1,1,1,0,NULL,NULL,'completed',NULL,'2025-07-08 09:38:12.505277','2025-07-20 07:03:02.134274',NULL);
INSERT INTO portfolio VALUES(2,'CRM-бот для управления клиентами',NULL,'Бот для автоматизации работы с клиентами, ведения базы данных и отправки рассылок','telegram_bot',NULL,'[]','Python, PostgreSQL, Redis, AmoCRM API','medium',8,21,NULL,'50000-70000',0,NULL,NULL,'[]',1,1,2,0,0,NULL,NULL,'completed',NULL,'2025-07-08 09:38:12.505282','2025-07-08 09:38:12.505283',NULL);
INSERT INTO portfolio VALUES(3,'Бот-опросник с аналитикой','','Интерактивный бот для проведения опросов с детальной аналитикой и экспортом результатов','telegram_bots',NULL,'[]','Python, Chart.js, Excel API, Google Sheets','medium',5,10,NULL,'',0,'','','[]',0,1,3,0,0,'','','completed',NULL,'2025-07-08 09:38:12.505285','2025-07-12 23:11:11.492716',NULL);
INSERT INTO portfolio VALUES(4,'оузукза','зшгзшгшгшпг','кукаау','web_development','main/3aae1480-e4ba-486e-82a7-0d7b59f6a04f.jpg','[]','','medium',5,10,150000.0,'',0,'','','[]',1,1,0,3,0,'','','completed',NULL,'2025-07-16 15:53:39.945715','2025-08-02 09:30:27.505723',NULL);
CREATE TABLE reviews (
	id INTEGER NOT NULL, 
	client_name VARCHAR(200) NOT NULL, 
	project_title VARCHAR(300) NOT NULL, 
	rating INTEGER NOT NULL, 
	review_text TEXT, 
	image_path VARCHAR(500), 
	is_visible BOOLEAN, 
	sort_order INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE faq (
	id INTEGER NOT NULL, 
	question TEXT NOT NULL, 
	answer TEXT NOT NULL, 
	category VARCHAR(100), 
	views_count INTEGER, 
	is_visible BOOLEAN, 
	sort_order INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO faq VALUES(1,'Сколько стоит разработка Telegram-бота?','Стоимость зависит от сложности проекта. Простой бот от 10,000₽, средний от 25,000₽, сложный от 50,000₽. Точную стоимость можно рассчитать с помощью калькулятора или создав ТЗ.','pricing',0,1,1,'2025-07-08 09:38:12.468019','2025-07-08 09:38:12.468022');
INSERT INTO faq VALUES(2,'Сколько времени занимает разработка?','Простой бот - 3-7 дней, средний - 1-2 недели, сложный - 2-4 недели. Сроки зависят от функционала и загруженности.','timeline',0,1,2,'2025-07-08 09:38:12.468024','2025-07-08 09:38:12.468025');
INSERT INTO faq VALUES(3,'Предоставляете ли вы техническую поддержку?','Да, предоставляем техническую поддержку и обслуживание ботов. Первый месяц поддержки бесплатно, далее от 2,000₽/месяц.','support',0,1,3,'2025-07-08 09:38:12.468026','2025-07-08 09:38:12.468027');
INSERT INTO faq VALUES(4,'Можете ли интегрировать бота с CRM или другими системами?','Конечно! Интегрируем с популярными CRM (AmoCRM, Bitrix24), платежными системами, базами данных и API сторонних сервисов.','integration',0,1,4,'2025-07-08 09:38:12.468028','2025-07-08 09:38:12.468029');
INSERT INTO faq VALUES(5,'Разрабатываете ли ботов для других платформ?','Да, разрабатываем ботов для Telegram, WhatsApp, ВКонтакте, веб-чатботов для сайтов и голосовых помощников.','platforms',0,1,5,'2025-07-08 09:38:12.468030','2025-07-08 09:38:12.468031');
CREATE TABLE settings (
	id INTEGER NOT NULL, 
	"key" VARCHAR(100) NOT NULL, 
	value TEXT, 
	description TEXT, 
	data_type VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE ("key")
);
INSERT INTO settings VALUES(1,'welcome_message','👋 Добро пожаловать! Я бот-визитка разработчика ботов. Помогу создать техническое задание для вашего проекта!','Приветственное сообщение','string','2025-07-08 09:38:12.506170','2025-07-08 09:38:12.506172');
INSERT INTO settings VALUES(2,'company_name','BotDev Studio','Название компании','string','2025-07-08 09:38:12.506173','2025-07-08 09:38:12.506174');
INSERT INTO settings VALUES(3,'contact_email','info@botdev.studio','Email для связи','string','2025-07-08 09:38:12.506174','2025-07-08 09:38:12.506175');
INSERT INTO settings VALUES(4,'contact_phone','+7 (999) 123-45-67','Телефон для связи','string','2025-07-08 09:38:12.506176','2025-07-08 09:38:12.506177');
INSERT INTO settings VALUES(5,'working_hours','Пн-Пт 9:00-18:00 (МСК)','Рабочие часы','string','2025-07-08 09:38:12.506178','2025-07-08 09:38:12.506179');
CREATE TABLE admin_users (
	id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	email VARCHAR(255), 
	first_name VARCHAR(255), 
	last_name VARCHAR(255), 
	role VARCHAR(50) NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	last_login DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO admin_users VALUES(1,'admin','cb872de2c8e7435bad0db5ce42b95b6e0ee8d27a8b1e0b9e10f5c1d9c8c4c8b6',NULL,'Администратор',NULL,'owner',1,NULL,NULL);
INSERT INTO admin_users VALUES(2,'Nikola','5038194010abdce978a068450eaa22261ce3fc7aaf19cacb88c4ce8e6c16a5a3','nikolaevnikolaj810@gmail.com','Николаев','Николай','executor',1,'2025-07-19 10:15:00.636179','2025-08-06 07:38:18.011262');
INSERT INTO admin_users VALUES(3,'Casper123','3397834ad24de801a18ee0b211539eae500c7e84e677f86bcc6a36858303c900','kluchka619@gmail.com','Миша','Ключка','executor',1,'2025-07-20 21:31:48.856121',NULL);
INSERT INTO admin_users VALUES(4,'daniltechno ','fd811e28b8d52cd1e6bdd1e944b0a5e6f7ae8fc417d553560b0d20cd62f3f270','hauslerreiner85@gmail.com','Даниил ','Михайлов','executor',1,'2025-07-23 05:31:02.673087',NULL);
INSERT INTO admin_users VALUES(5,'xfce0','ed34e117a4df253203b339bb0821f6b2836924e9ff8fdd52eb1bc2d07e44c91b','pavlinborisich@gmail.com','Павел','','executor',1,'2025-07-23 05:35:42.252919',NULL);
INSERT INTO admin_users VALUES(6,'testexecutor','ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',NULL,'Тестовый Исполнитель',NULL,'executor',1,'2025-08-02 00:13:37.570629',NULL);
INSERT INTO admin_users VALUES(7,'gennic','c0c4a69b17a7955ac230bfc8db4a123eaa956ccf3c0022e68b8d4e2f5b699d1f','gennic@yandex.ru','Геннадий','Николаев','executor',1,'2025-08-03 10:02:35.247265',NULL);
CREATE TABLE projects (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	original_request TEXT, 
	structured_tz JSON, 
	status VARCHAR(50), 
	priority VARCHAR(20), 
	project_type VARCHAR(50), 
	complexity VARCHAR(20), 
	estimated_cost FLOAT, 
	executor_cost FLOAT, 
	final_cost FLOAT, 
	estimated_hours INTEGER, 
	actual_hours INTEGER, 
	deadline DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	project_metadata JSON, 
	assigned_executor_id INTEGER, 
	assigned_at DATETIME, prepayment_amount REAL DEFAULT 0.0, client_paid_total REAL DEFAULT 0.0, executor_paid_total REAL DEFAULT 0.0, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(assigned_executor_id) REFERENCES admin_users (id)
);
INSERT INTO projects VALUES(8,25,'Telegram-бот для контента и новостей',replace('📋 НАЗВАНИЕ ПРОЕКТА\nTelegram-бот для контента и новостей\n\n📝 ОПИСАНИЕ ПРОЕКТА\nАвтоматизированный бот для публикации и управления контентом с возможностью подписки на различные категории, поиска материалов и интерактивного взаимодействия с аудиторией.\n\n🎯 ЦЕЛИ И ЗАДАЧИ\n• Автоматизация бизнес-процессов через Telegram\n• Улучшение клиентского опыта\n• Снижение нагрузки на персонал\n• Увеличение конверсии и продаж\n• Создание дополнительного канала коммуникации\n\n👥 ЦЕЛЕВАЯ АУДИТОРИЯ\nОсновная аудитория: активные пользователи Telegram в возрасте 18-45 лет\nДополнительная аудитория: клиенты, предпочитающие быстрое и удобное обслуживание\n\n⚙️ ОСНОВНЫЕ ФУНКЦИИ\n• Публикация новостей и статей\n• Категоризация контента\n• Подписка на темы\n• Поиск по материалам\n• Комментарии и реакции\n• Рассылки по расписанию\n• Статистика просмотров\n• Админка для управления контентом\n\n🔧 ТЕХНИЧЕСКИЙ СТЕК\n• Python 3.9+\n• aiogram 3.x / python-telegram-bot\n• PostgreSQL для основной БД\n• Redis для кеширования\n• Docker для контейнер...','\n',char(10)),NULL,'{"title": "Telegram-\u0431\u043e\u0442 \u0434\u043b\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430 \u0438 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439", "description": "\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0431\u043e\u0442 \u0434\u043b\u044f \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438 \u0438 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c \u0441 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c\u044e \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438 \u043d\u0430 \u0440\u0430\u0437\u043b\u0438\u0447\u043d\u044b\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438, \u043f\u043e\u0438\u0441\u043a\u0430 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u0432 \u0438 \u0438\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u0432\u0437\u0430\u0438\u043c\u043e\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0441 \u0430\u0443\u0434\u0438\u0442\u043e\u0440\u0438\u0435\u0439.", "goals": "\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u044f \u0431\u0438\u0437\u043d\u0435\u0441-\u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432 \u0438 \u0443\u043b\u0443\u0447\u0448\u0435\u043d\u0438\u0435 \u043a\u043b\u0438\u0435\u043d\u0442\u0441\u043a\u043e\u0433\u043e \u043e\u043f\u044b\u0442\u0430", "target_audience": "\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 Telegram \u0432 \u0432\u043e\u0437\u0440\u0430\u0441\u0442\u0435 18-45 \u043b\u0435\u0442", "tz_text": "\ud83d\udccb \u041d\u0410\u0417\u0412\u0410\u041d\u0418\u0415 \u041f\u0420\u041e\u0415\u041a\u0422\u0410\nTelegram-\u0431\u043e\u0442 \u0434\u043b\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430 \u0438 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439\n\n\ud83d\udcdd \u041e\u041f\u0418\u0421\u0410\u041d\u0418\u0415 \u041f\u0420\u041e\u0415\u041a\u0422\u0410\n\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0431\u043e\u0442 \u0434\u043b\u044f \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438 \u0438 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c \u0441 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c\u044e \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438 \u043d\u0430 \u0440\u0430\u0437\u043b\u0438\u0447\u043d\u044b\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438, \u043f\u043e\u0438\u0441\u043a\u0430 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u0432 \u0438 \u0438\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u0432\u0437\u0430\u0438\u043c\u043e\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0441 \u0430\u0443\u0434\u0438\u0442\u043e\u0440\u0438\u0435\u0439.\n\n\ud83c\udfaf \u0426\u0415\u041b\u0418 \u0418 \u0417\u0410\u0414\u0410\u0427\u0418\n\u2022 \u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u044f \u0431\u0438\u0437\u043d\u0435\u0441-\u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u0432 \u0447\u0435\u0440\u0435\u0437 Telegram\n\u2022 \u0423\u043b\u0443\u0447\u0448\u0435\u043d\u0438\u0435 \u043a\u043b\u0438\u0435\u043d\u0442\u0441\u043a\u043e\u0433\u043e \u043e\u043f\u044b\u0442\u0430\n\u2022 \u0421\u043d\u0438\u0436\u0435\u043d\u0438\u0435 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438 \u043d\u0430 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\n\u2022 \u0423\u0432\u0435\u043b\u0438\u0447\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0432\u0435\u0440\u0441\u0438\u0438 \u0438 \u043f\u0440\u043e\u0434\u0430\u0436\n\u2022 \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u043a\u0430\u043d\u0430\u043b\u0430 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438\n\n\ud83d\udc65 \u0426\u0415\u041b\u0415\u0412\u0410\u042f \u0410\u0423\u0414\u0418\u0422\u041e\u0420\u0418\u042f\n\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0430\u0443\u0434\u0438\u0442\u043e\u0440\u0438\u044f: \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 Telegram \u0432 \u0432\u043e\u0437\u0440\u0430\u0441\u0442\u0435 18-45 \u043b\u0435\u0442\n\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0430\u0443\u0434\u0438\u0442\u043e\u0440\u0438\u044f: \u043a\u043b\u0438\u0435\u043d\u0442\u044b, \u043f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u044e\u0449\u0438\u0435 \u0431\u044b\u0441\u0442\u0440\u043e\u0435 \u0438 \u0443\u0434\u043e\u0431\u043d\u043e\u0435 \u043e\u0431\u0441\u043b\u0443\u0436\u0438\u0432\u0430\u043d\u0438\u0435\n\n\u2699\ufe0f \u041e\u0421\u041d\u041e\u0412\u041d\u042b\u0415 \u0424\u0423\u041d\u041a\u0426\u0418\u0418\n\u2022 \u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439\n\u2022 \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430\n\u2022 \u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b\n\u2022 \u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c\n\u2022 \u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438\n\u2022 \u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e\n\u2022 \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432\n\u2022 \u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c\n\n\ud83d\udd27 \u0422\u0415\u0425\u041d\u0418\u0427\u0415\u0421\u041a\u0418\u0419 \u0421\u0422\u0415\u041a\n\u2022 Python 3.9+\n\u2022 aiogram 3.x / python-telegram-bot\n\u2022 PostgreSQL \u0434\u043b\u044f \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0411\u0414\n\u2022 Redis \u0434\u043b\u044f \u043a\u0435\u0448\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f\n\u2022 Docker \u0434\u043b\u044f \u043a\u043e\u043d\u0442\u0435\u0439\u043d\u0435\u0440\u0438\u0437\u0430\u0446\u0438\u0438\n\u2022 FastAPI \u0434\u043b\u044f \u0430\u0434\u043c\u0438\u043d-\u043f\u0430\u043d\u0435\u043b\u0438\n\u2022 Nginx \u0434\u043b\u044f \u043f\u0440\u043e\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f\n\n\ud83d\udd17 \u0418\u041d\u0422\u0415\u0413\u0420\u0410\u0426\u0418\u0418\n\u2022 Telegram Bot API\n\u2022 \u041f\u043b\u0430\u0442\u0435\u0436\u043d\u044b\u0435 \u0441\u0438\u0441\u0442\u0435\u043c\u044b (\u042eKassa, Stripe)\n\u2022 SMS-\u0441\u0435\u0440\u0432\u0438\u0441\u044b \u0434\u043b\u044f \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0439\n\u2022 \u0412\u043d\u0435\u0448\u043d\u0438\u0435 API \u043f\u043e \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044e\n\u2022 \u0421\u0438\u0441\u0442\u0435\u043c\u044b \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438\n\n\ud83d\udcca \u0410\u0414\u041c\u0418\u041d-\u041f\u0410\u041d\u0415\u041b\u042c\n\u2022 \u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c\u0438 \u0438 \u0438\u0445 \u043f\u0440\u0430\u0432\u0430\u043c\u0438\n\u2022 \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u043e\u0442\u0430\n\u2022 \u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u043c\u0438\n\u2022 \u041e\u0442\u0447\u0435\u0442\u044b \u0438 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430\n\u2022 \u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u0440\u0430\u0431\u043e\u0442\u044b \u0441\u0438\u0441\u0442\u0435\u043c\u044b\n\n\ud83d\udcc8 \u042d\u0422\u0410\u041f\u042b \u0420\u0410\u0417\u0420\u0410\u0411\u041e\u0422\u041a\u0418\n1. \u041f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u044b (3 \u0434\u043d\u044f)\n2. \u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430 MVP \u0444\u0443\u043d\u043a\u0446\u0438\u0439 (7 \u0434\u043d\u0435\u0439)\n3. \u0418\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u044f \u0441 \u0432\u043d\u0435\u0448\u043d\u0438\u043c\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430\u043c\u0438 (5 \u0434\u043d\u0435\u0439)\n4. \u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0430\u0434\u043c\u0438\u043d-\u043f\u0430\u043d\u0435\u043b\u0438 (5 \u0434\u043d\u0435\u0439)\n5. \u0422\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0438 \u043e\u0442\u043b\u0430\u0434\u043a\u0430 (3 \u0434\u043d\u044f)\n6. \u0414\u0435\u043f\u043b\u043e\u0439 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 (2 \u0434\u043d\u044f)\n\n\u26a0\ufe0f \u0420\u0418\u0421\u041a\u0418 \u0418 \u0421\u041b\u041e\u0416\u041d\u041e\u0421\u0422\u0418\n\u2022 \u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f Telegram Bot API\n\u2022 \u041d\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043f\u0440\u0438 \u0431\u043e\u043b\u044c\u0448\u043e\u043c \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439\n\u2022 \u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0432 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f\u0445 \u043f\u043b\u0430\u0442\u0435\u0436\u043d\u044b\u0445 \u0441\u0438\u0441\u0442\u0435\u043c\n\u2022 \u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u044c \u0441\u043e\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u0439 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438\n\u2022 \u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c \u0432 \u043c\u0430\u0441\u0448\u0442\u0430\u0431\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438 \u043f\u0440\u0438 \u0440\u043e\u0441\u0442\u0435 \u0430\u0443\u0434\u0438\u0442\u043e\u0440\u0438\u0438\n\n\u23f1\ufe0f \u0412\u0420\u0415\u041c\u0415\u041d\u041d\u042b\u0415 \u0420\u0410\u041c\u041a\u0418\n\u041e\u0431\u0449\u0435\u0435 \u0432\u0440\u0435\u043c\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438: 50 \u0447\u0430\u0441\u043e\u0432\n\u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f: 3-4 \u043d\u0435\u0434\u0435\u043b\u0438\n\u0412\u043a\u043b\u044e\u0447\u0430\u0435\u0442: \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0443, \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435, \u0434\u0435\u043f\u043b\u043e\u0439\n\n\ud83d\udcb0 \u041f\u0420\u0418\u041c\u0415\u0420\u041d\u0410\u042f \u0421\u0422\u041e\u0418\u041c\u041e\u0421\u0422\u042c\n\u0411\u0430\u0437\u043e\u0432\u0430\u044f \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c: 75,000 \u0440\u0443\u0431\u043b\u0435\u0439\n\u0414\u0438\u0430\u043f\u0430\u0437\u043e\u043d: 63,750 - 86,250 \u0440\u0443\u0431\u043b\u0435\u0439\n\u0421\u0442\u0430\u0432\u043a\u0430: 1500\u20bd/\u0447\u0430\u0441\n\n\ud83d\ude80 MVP \u0424\u0423\u041d\u041a\u0426\u0418\u0418\n\u2022 \u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439\n\u2022 \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430\n\u2022 \u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b\n\u2022 \u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c\n\n\u2795 \u0414\u041e\u041f\u041e\u041b\u041d\u0418\u0422\u0415\u041b\u042c\u041d\u042b\u0415 \u0412\u041e\u0417\u041c\u041e\u0416\u041d\u041e\u0421\u0422\u0418\n\u2022 \u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438\n\u2022 \u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e\n\u2022 \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432\n\u2022 \u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c\n\u2022 \u041c\u0443\u043b\u044c\u0442\u0438\u044f\u0437\u044b\u0447\u043d\u043e\u0441\u0442\u044c\n\u2022 \u0418\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u044f \u0441 CRM\n\u2022 \u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430\n\u2022 \u041f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430", "bot_sections": [{"section_name": "\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c", "description": "\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0444\u0443\u043d\u043a\u0446\u0438\u0438 \u0431\u043e\u0442\u0430", "functions": ["\u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439", "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430", "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b", "\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c", "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438", "\u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e", "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432", "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c"], "complexity_level": "medium", "estimated_hours": 50}], "detailed_functions": [{"function_name": "\u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}, {"function_name": "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c", "description": "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f: \u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c", "user_flow": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0439", "technical_requirements": "\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u044b", "complexity_risks": "\u0420\u0438\u0441\u043a\u0438 \u043e\u0446\u0435\u043d\u0435\u043d\u044b \u0438 \u0443\u0447\u0442\u0435\u043d\u044b \u0432 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "estimated_hours": 8}], "technology_stack": {"language": "Python", "framework": "aiogram 3.x", "database": "PostgreSQL", "additional_tools": ["Redis", "Docker", "FastAPI"], "external_apis": ["Telegram Bot API", "Payment APIs"]}, "integrations": [{"name": "Telegram Bot API", "purpose": "\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0431\u043e\u0442\u0430", "complexity": "medium", "estimated_hours": 5}, {"name": "\u041f\u043b\u0430\u0442\u0435\u0436\u043d\u044b\u0435 \u0441\u0438\u0441\u0442\u0435\u043c\u044b", "purpose": "\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043f\u043b\u0430\u0442\u0435\u0436\u0435\u0439", "complexity": "high", "estimated_hours": 10}], "admin_panel_requirements": {"needed": true, "functions": ["\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c\u0438", "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0438 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430", "\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c", "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0431\u043e\u0442\u0430"], "estimated_hours": 20}, "development_stages": [{"stage": "\u042d\u0442\u0430\u043f 1: \u041f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435", "description": "\u0414\u0435\u0442\u0430\u043b\u044c\u043d\u043e\u0435 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0430\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u044b", "deliverables": ["\u0422\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u044f", "\u0421\u0445\u0435\u043c\u0430 \u0411\u0414"], "duration_days": 3, "hours": 15}, {"stage": "\u042d\u0442\u0430\u043f 2: \u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430 MVP", "description": "\u0420\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f \u043e\u0441\u043d\u043e\u0432\u043d\u044b\u0445 \u0444\u0443\u043d\u043a\u0446\u0438\u0439", "deliverables": ["\u0420\u0430\u0431\u043e\u0447\u0438\u0439 MVP", "\u0411\u0430\u0437\u043e\u0432\u044b\u0435 \u0442\u0435\u0441\u0442\u044b"], "duration_days": 7, "hours": 25}], "complexity_analysis": {"overall_complexity": "medium", "complex_features": ["\u0418\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u0438 \u0441 \u0432\u043d\u0435\u0448\u043d\u0438\u043c\u0438 API", "\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043f\u043b\u0430\u0442\u0435\u0436\u0435\u0439"], "simple_features": ["\u0411\u0430\u0437\u043e\u0432\u044b\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u044b", "\u041f\u0440\u043e\u0441\u0442\u044b\u0435 \u043e\u0442\u0432\u0435\u0442\u044b"], "integration_complexity": "\u0421\u0440\u0435\u0434\u043d\u044f\u044f \u0441\u043b\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u0438\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u0439"}, "risks_and_challenges": [{"risk": "\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f Telegram Bot API", "impact": "medium", "mitigation": "\u0418\u0437\u0443\u0447\u0435\u043d\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430\u0446\u0438\u0438 \u0438 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u043e\u0431\u0445\u043e\u0434\u043d\u044b\u0445 \u043f\u0443\u0442\u0435\u0439"}, {"risk": "\u041c\u0430\u0441\u0448\u0442\u0430\u0431\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u0438 \u0440\u043e\u0441\u0442\u0435 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438", "impact": "high", "mitigation": "\u041f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0441 \u0443\u0447\u0435\u0442\u043e\u043c \u043c\u0430\u0441\u0448\u0442\u0430\u0431\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f"}], "estimated_hours": 50, "priority_features": ["\u041f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439", "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430", "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0442\u0435\u043c\u044b", "\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430\u043c"], "optional_features": ["\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438 \u0438 \u0440\u0435\u0430\u043a\u0446\u0438\u0438", "\u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044e", "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432", "\u0410\u0434\u043c\u0438\u043d\u043a\u0430 \u0434\u043b\u044f \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c", "\u041c\u0443\u043b\u044c\u0442\u0438\u044f\u0437\u044b\u0447\u043d\u043e\u0441\u0442\u044c", "\u0418\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u044f \u0441 CRM"]}','in_progress','normal','web','medium',50000.0,25000.0,50000.0,50,NULL,'2025-08-10 13:13:00.000000','2025-08-03 08:59:12.993839','2025-08-03 10:13:31.313702','{"status_history": [{"from_status": "new", "to_status": "\u0432_\u0440\u0430\u0431\u043e\u0442\u0435", "from_status_name": "\u041d\u043e\u0432\u044b\u0439", "to_status_name": "\u0412 \u0440\u0430\u0431\u043e\u0442\u0435", "changed_at": "2025-08-03T09:21:12.478197", "comment": "\u041f\u0440\u0438\u0441\u0442\u0443\u043f\u0430\u044e \u043a \u0440\u0430\u0431\u043e\u0442\u0435!", "changed_by": "admin"}]}',7,NULL,25000.0,25000.0,25000.0);
CREATE TABLE consultant_sessions (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_id VARCHAR(100) NOT NULL, 
	topic VARCHAR(200), 
	status VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, 
	expires_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (session_id)
);
CREATE TABLE messages (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	project_id INTEGER, 
	message_text TEXT, 
	message_type VARCHAR(50), 
	sender_type VARCHAR(20), 
	file_path VARCHAR(500), 
	is_read BOOLEAN, 
	thread_id VARCHAR(100), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
CREATE TABLE consultant_queries (
	id INTEGER NOT NULL, 
	session_id INTEGER NOT NULL, 
	user_query TEXT NOT NULL, 
	ai_response TEXT, 
	tokens_used INTEGER, 
	response_time FLOAT, 
	created_at DATETIME, 
	rating INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES consultant_sessions (id)
);
CREATE TABLE files (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	user_id INTEGER NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	original_name VARCHAR(255) NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	file_type VARCHAR(50) NOT NULL, 
	file_size INTEGER, 
	upload_date DATETIME, 
	file_metadata JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE project_files (
	id INTEGER NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	original_filename VARCHAR(255) NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	file_size INTEGER NOT NULL, 
	file_type VARCHAR(100) NOT NULL, 
	description TEXT, 
	uploaded_at DATETIME, 
	project_id INTEGER NOT NULL, 
	uploaded_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(uploaded_by_id) REFERENCES admin_users (id)
);
CREATE TABLE project_statuses (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	color VARCHAR(7), 
	icon VARCHAR(50), 
	is_default BOOLEAN, 
	is_active BOOLEAN, 
	sort_order INTEGER, 
	created_at DATETIME, 
	created_by_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO project_statuses VALUES(1,'Новый','Проект только что создан и ожидает рассмотрения','#007bff','fas fa-plus-circle',1,1,1,'2025-07-09 07:33:43.090827',NULL);
INSERT INTO project_statuses VALUES(2,'На рассмотрении','Проект рассматривается менеджером','#ffc107','fas fa-eye',1,1,2,'2025-07-09 07:33:43.090885',NULL);
INSERT INTO project_statuses VALUES(3,'Согласован','Проект согласован и готов к выполнению','#17a2b8','fas fa-check-circle',1,1,3,'2025-07-09 07:33:43.090907',NULL);
INSERT INTO project_statuses VALUES(4,'В работе','Проект находится в разработке','#fd7e14','fas fa-cogs',1,1,4,'2025-07-09 07:33:43.090922',NULL);
INSERT INTO project_statuses VALUES(5,'На тестировании','Проект проходит тестирование','#6f42c1','fas fa-bug',1,1,5,'2025-07-09 07:33:43.090933',NULL);
INSERT INTO project_statuses VALUES(6,'Завершен','Проект успешно завершен','#28a745','fas fa-check',1,1,6,'2025-07-09 07:33:43.090945',NULL);
INSERT INTO project_statuses VALUES(7,'Отменен','Проект отменен','#dc3545','fas fa-times-circle',1,1,7,'2025-07-09 07:33:43.090955',NULL);
INSERT INTO project_statuses VALUES(8,'Приостановлен','Проект временно приостановлен','#6c757d','fas fa-pause-circle',0,1,8,'2025-07-09 07:54:48.580186',1);
INSERT INTO project_statuses VALUES(9,'Тестовый статус','Тест кастомного статуса','#ff5733','fas fa-test',0,1,10,'2025-07-09 08:14:41.155507',1);
INSERT INTO project_statuses VALUES(10,'админ консоль готова','Кастомный статус: админ консоль готова','#6c757d','fas fa-circle',0,1,999,'2025-07-09 08:21:05.344299',1);
CREATE TABLE project_status_logs (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	status_id INTEGER NOT NULL, 
	previous_status_id INTEGER, 
	comment TEXT, 
	changed_at DATETIME, 
	changed_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(status_id) REFERENCES project_statuses (id), 
	FOREIGN KEY(previous_status_id) REFERENCES project_statuses (id), 
	FOREIGN KEY(changed_by_id) REFERENCES admin_users (id)
);
CREATE TABLE finance_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	description TEXT, 
	color VARCHAR(7), 
	icon VARCHAR(50), 
	is_active BOOLEAN, 
	created_at DATETIME, 
	created_by_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO finance_categories VALUES(1,'Проекты - Разработка ботов','income','Доходы от разработки Telegram-ботов','#28a745','🤖',1,'2025-07-10 17:57:04.297857',1);
INSERT INTO finance_categories VALUES(2,'Проекты - Веб-разработка','income','Доходы от веб-разработки','#17a2b8','🌐',1,'2025-07-10 17:57:04.297920',1);
INSERT INTO finance_categories VALUES(3,'Консультации','income','Доходы от консультаций','#20c997','🤝',1,'2025-07-10 17:57:04.297940',1);
INSERT INTO finance_categories VALUES(4,'Дополнительные услуги','income','Настройка серверов, домены и прочее','#6f42c1','🛠️',1,'2025-07-10 17:57:04.297953',1);
INSERT INTO finance_categories VALUES(5,'Бонусы и премии','income','Бонусные выплаты от клиентов','#fd7e14','🎁',1,'2025-07-10 17:57:04.297964',1);
INSERT INTO finance_categories VALUES(6,'Выплаты исполнителям','expense','Оплата работы исполнителей','#dc3545','👥',1,'2025-07-10 17:57:04.297984',1);
INSERT INTO finance_categories VALUES(7,'Нейросети и API','expense','Расходы на OpenAI, Claude и другие AI-сервисы','#e83e8c','🧠',1,'2025-07-10 17:57:04.297996',1);
INSERT INTO finance_categories VALUES(8,'Хостинг и серверы','expense','Оплата хостинга, VPS, доменов','#6c757d','🖥️',1,'2025-07-10 17:57:04.298005',1);
INSERT INTO finance_categories VALUES(9,'Лицензии и подписки','expense','Софт, инструменты разработки','#007bff','🔑',1,'2025-07-10 17:57:04.298015',1);
INSERT INTO finance_categories VALUES(10,'Реклама и маркетинг','expense','Расходы на продвижение','#ffc107','📢',1,'2025-07-10 17:57:04.298024',1);
INSERT INTO finance_categories VALUES(11,'Офисные расходы','expense','Интернет, электричество, прочие расходы','#6f42c1','📊',1,'2025-07-10 17:57:04.298033',1);
INSERT INTO finance_categories VALUES(12,'Налоги и сборы','expense','Налоги, комиссии банков','#dc3545','📋',1,'2025-07-10 17:57:04.298042',1);
INSERT INTO finance_categories VALUES(13,'Обучение и развитие','expense','Курсы, книги, конференции','#17a2b8','🎓',1,'2025-07-10 17:57:04.298052',1);
CREATE TABLE finance_transactions (
	id INTEGER NOT NULL, 
	amount FLOAT NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	description TEXT NOT NULL, 
	date DATETIME NOT NULL, 
	category_id INTEGER NOT NULL, 
	project_id INTEGER, 
	contractor_name VARCHAR(255), 
	receipt_url VARCHAR(500), 
	notes TEXT, 
	is_recurring BOOLEAN, 
	recurring_period VARCHAR(50), 
	parent_transaction_id INTEGER, 
	created_at DATETIME, 
	created_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES finance_categories (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(parent_transaction_id) REFERENCES finance_transactions (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO finance_transactions VALUES(8,750.0,'income','Финальная тестовая транзакция','2025-01-18 14:00:00.000000',1,NULL,NULL,NULL,'Проверяем работу кнопок удаления',0,NULL,NULL,'2025-07-17 22:35:28.167054',2);
INSERT INTO finance_transactions VALUES(9,40000.0,'income','Бот разработка @truetechshop предоплата 40.000 из 80.000','2025-07-18 15:06:00.000000',1,NULL,'Николай',NULL,NULL,0,NULL,NULL,'2025-07-18 15:07:40.896845',2);
INSERT INTO finance_transactions VALUES(10,20000.0,'income','Предоплата за бота по Удержаниям Роман (телеграм pythongodbless) там искать сумма 20000 из 45000','2025-07-20 09:36:00.000000',1,NULL,'Никола',NULL,NULL,0,NULL,NULL,'2025-07-20 09:37:53.016062',2);
INSERT INTO finance_transactions VALUES(11,50000.0,'income','оплата вторая часть за ITCOIN 50000 (остаток 30000)','2025-07-21 14:25:00.000000',1,NULL,'Паша',NULL,NULL,0,NULL,NULL,'2025-07-21 14:26:03.472857',2);
INSERT INTO finance_transactions VALUES(12,40000.0,'income','Бот по продаже цифровых товаров 40000 ( выплаачено 80000 из 80000)','2025-07-23 22:13:00.000000',1,NULL,'Никола',NULL,NULL,0,NULL,NULL,'2025-07-23 22:14:48.702278',2);
INSERT INTO finance_transactions VALUES(13,25000.0,'income','Транзакция из чека receipt_501613334_1754291781.jpg','2025-08-03 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291781.jpg','OCR данные: {"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:16:37.171025',2);
INSERT INTO finance_transactions VALUES(14,10000.0,'income','Транзакция из чека receipt_501613334_1754291804.jpg','2025-07-30 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291804.jpg','OCR данные: {"success": true, "amount": 10000.0, "date": "2025-07-30T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": \"10000\",\n    \"date\": \"30.07.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1.0\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:17:02.660866',2);
INSERT INTO finance_transactions VALUES(15,80000.0,'income','Транзакция из чека receipt_501613334_1754291831.jpg','2025-08-01 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291831.jpg','OCR данные: {"success": true, "amount": 80000.0, "date": "2025-08-01T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 80000,\n    \"date\": \"01.08.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:17:19.358795',2);
INSERT INTO finance_transactions VALUES(16,5000.0,'expense','Транзакция из чека receipt_501613334_1754298071.jpg','2025-08-04 00:00:00.000000',10,NULL,NULL,'uploads/receipts/receipt_501613334_1754298071.jpg','OCR данные: {"success": true, "amount": 5000.0, "date": "2025-08-04T00:00:00", "organization": "ООО \"КЕХ ЭКОММЕРЦ\"", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 5000,\n    \"date\": \"04.08.2025\",\n    \"organization\": \"ООО \\\"КЕХ ЭКОММЕРЦ\\\"\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 09:01:26.806392',2);
CREATE TABLE finance_budgets (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	category_id INTEGER NOT NULL, 
	planned_amount FLOAT NOT NULL, 
	period_start DATETIME NOT NULL, 
	period_end DATETIME NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	created_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES finance_categories (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
CREATE TABLE contractors (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	contact_info JSON, 
	skills JSON, 
	hourly_rate FLOAT, 
	project_rate FLOAT, 
	rating FLOAT, 
	status VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO contractors VALUES(1,'Алексей Иванов','Опытный Python-разработчик, специализируется на создании Telegram-ботов','{"email": "alexey.ivanov@email.com", "phone": "+7 (999) 123-45-67", "telegram": "@alexey_dev"}','["Python", "Telegram Bot API", "PostgreSQL", "FastAPI", "Docker"]',2000.0,25000.0,4.799999999999999823,'active','2025-07-09 09:11:54.699613','2025-07-09 09:11:54.699617');
INSERT INTO contractors VALUES(2,'Мария Петрова','Frontend-разработчик с опытом создания веб-интерфейсов','{"email": "maria.petrova@email.com", "phone": "+7 (999) 234-56-78", "telegram": "@maria_frontend"}','["HTML", "CSS", "JavaScript", "React", "Vue.js", "Bootstrap"]',1500.0,20000.0,4.599999999999999644,'active','2025-07-09 09:11:54.699618','2025-07-09 09:11:54.699618');
INSERT INTO contractors VALUES(3,'Дмитрий Козлов','Fullstack-разработчик, работает с различными технологиями','{"email": "dmitry.kozlov@email.com", "phone": "+7 (999) 345-67-89", "telegram": "@dmitry_fullstack"}','["Python", "JavaScript", "Node.js", "React", "PostgreSQL", "MongoDB"]',2500.0,35000.0,4.900000000000000355,'active','2025-07-09 09:11:54.699619','2025-07-09 09:11:54.699619');
INSERT INTO contractors VALUES(4,'Елена Смирнова','UI/UX дизайнер с большим опытом в создании пользовательских интерфейсов','{"email": "elena.smirnova@email.com", "phone": "+7 (999) 456-78-90", "telegram": "@elena_design"}','["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator"]',1800.0,15000.0,4.700000000000000177,'active','2025-07-09 09:11:54.699620','2025-07-09 09:11:54.699620');
INSERT INTO contractors VALUES(5,'Андрей Волков','DevOps-инженер, настройка серверов и CI/CD','{"email": "andrey.volkov@email.com", "phone": "+7 (999) 567-89-01", "telegram": "@andrey_devops"}','["Docker", "Kubernetes", "AWS", "Linux", "Nginx", "Jenkins"]',3000.0,40000.0,4.799999999999999823,'active','2025-07-09 09:11:54.699621','2025-07-09 09:11:54.699621');
INSERT INTO contractors VALUES(6,'Ольга Лебедева','QA-инженер, тестирование веб-приложений и мобильных приложений','{"email": "olga.lebedeva@email.com", "phone": "+7 (999) 678-90-12", "telegram": "@olga_qa"}','["Manual Testing", "Automated Testing", "Selenium", "Postman", "Jest"]',1200.0,12000.0,4.5,'active','2025-07-09 09:11:54.699622','2025-07-09 09:11:54.699622');
INSERT INTO contractors VALUES(7,'Игорь Новиков','Мобильный разработчик, создание iOS и Android приложений','{"email": "igor.novikov@email.com", "phone": "+7 (999) 789-01-23", "telegram": "@igor_mobile"}','["Swift", "Kotlin", "Flutter", "React Native", "iOS", "Android"]',2200.0,30000.0,4.599999999999999644,'active','2025-07-09 09:11:54.699622','2025-07-09 09:11:54.699623');
INSERT INTO contractors VALUES(8,'Татьяна Морозова','Контент-менеджер и копирайтер','{"email": "tatyana.morozova@email.com", "phone": "+7 (999) 890-12-34", "telegram": "@tatyana_content"}','["Copywriting", "Content Management", "SEO", "Social Media"]',800.0,8000.0,4.400000000000000356,'active','2025-07-09 09:11:54.699623','2025-07-09 09:11:54.699623');
INSERT INTO contractors VALUES(9,'Владимир Сидоров','Консультант по IT-проектам (временно неактивен)','{"email": "vladimir.sidorov@email.com", "phone": "+7 (999) 901-23-45", "telegram": "@vladimir_consultant"}','["Project Management", "Business Analysis", "Agile", "Scrum"]',2800.0,50000.0,4.299999999999999823,'inactive','2025-07-09 09:11:54.699624','2025-07-09 09:11:54.699624');
CREATE TABLE service_providers (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	provider_type VARCHAR(100) NOT NULL, 
	website VARCHAR(500), 
	contact_info JSON, 
	pricing_model VARCHAR(100), 
	status VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO service_providers VALUES(1,'OpenAI API','API для доступа к моделям GPT','ai','https://openai.com','{"email": "support@openai.com"}','usage','active','2025-07-09 09:10:35.989760','2025-07-09 09:10:35.989764');
INSERT INTO service_providers VALUES(2,'OpenRouter','API-роутер для различных AI моделей','ai','https://openrouter.ai','{"email": "support@openrouter.ai"}','usage','active','2025-07-09 09:10:35.989765','2025-07-09 09:10:35.989765');
INSERT INTO service_providers VALUES(3,'Claude API','API для доступа к моделям Claude от Anthropic','ai','https://www.anthropic.com','{"email": "support@anthropic.com"}','usage','active','2025-07-09 09:10:35.989766','2025-07-09 09:10:35.989766');
INSERT INTO service_providers VALUES(4,'DigitalOcean','Облачный хостинг и VPS','hosting','https://digitalocean.com','{"email": "support@digitalocean.com"}','monthly','active','2025-07-09 09:10:35.989766','2025-07-09 09:10:35.989767');
INSERT INTO service_providers VALUES(5,'Timeweb','Российский хостинг-провайдер','hosting','https://timeweb.com','{"email": "support@timeweb.ru", "phone": "+7 (495) 663-65-65"}','monthly','active','2025-07-09 09:10:35.989767','2025-07-09 09:10:35.989768');
INSERT INTO service_providers VALUES(6,'AWS S3','Облачное хранилище Amazon','storage','https://aws.amazon.com/s3/','{"email": "aws-support@amazon.com"}','usage','active','2025-07-09 09:10:35.989768','2025-07-09 09:10:35.989768');
INSERT INTO service_providers VALUES(7,'YooMoney','Платежная система (бывший Яндекс.Деньги)','payment','https://yoomoney.ru','{"email": "support@yoomoney.ru", "phone": "8 800 250-66-99"}','per_request','active','2025-07-09 09:10:35.989769','2025-07-09 09:10:35.989769');
INSERT INTO service_providers VALUES(8,'Telegram Bot API','API для разработки Telegram ботов','other','https://core.telegram.org/bots/api','{"email": "support@telegram.org"}','usage','active','2025-07-09 09:10:35.989769','2025-07-09 09:10:35.989770');
INSERT INTO service_providers VALUES(9,'Google Analytics','Веб-аналитика от Google','analytics','https://analytics.google.com','{"email": "support@google.com"}','usage','active','2025-07-09 09:10:35.989770','2025-07-09 09:10:35.989770');
INSERT INTO service_providers VALUES(10,'SendGrid','Email-сервис для рассылок','email','https://sendgrid.com','{"email": "support@sendgrid.com"}','usage','active','2025-07-09 09:10:35.989771','2025-07-09 09:10:35.989771');
INSERT INTO service_providers VALUES(11,'Cloudflare','CDN и защита сайтов','cdn','https://cloudflare.com','{"email": "support@cloudflare.com"}','monthly','active','2025-07-09 09:10:35.989771','2025-07-09 09:10:35.989772');
INSERT INTO service_providers VALUES(12,'SMS.ru','SMS-рассылки в России','sms','https://sms.ru','{"email": "support@sms.ru", "phone": "+7 (495) 545-45-67"}','per_request','active','2025-07-09 09:10:35.989772','2025-07-09 09:10:35.989772');
CREATE TABLE finance_reports (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	report_type VARCHAR(100) NOT NULL, 
	period_start DATETIME NOT NULL, 
	period_end DATETIME NOT NULL, 
	data JSON, 
	created_at DATETIME, 
	created_by_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
CREATE TABLE contractor_payments (
	id INTEGER NOT NULL, 
	contractor_id INTEGER NOT NULL, 
	project_id INTEGER, 
	amount FLOAT NOT NULL, 
	payment_type VARCHAR(50), 
	description TEXT, 
	payment_date DATETIME, 
	status VARCHAR(50), 
	payment_method VARCHAR(100), 
	created_at DATETIME, 
	created_by_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contractor_id) REFERENCES contractors (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO contractor_payments VALUES(1,2,NULL,5000.0,'project','выплата за бота','2025-07-19 10:28:08.267914','pending',NULL,'2025-07-19 10:28:08.265889',0);
CREATE TABLE service_expenses (
	id INTEGER NOT NULL, 
	service_provider_id INTEGER NOT NULL, 
	project_id INTEGER, 
	amount FLOAT NOT NULL, 
	expense_type VARCHAR(100) NOT NULL, 
	description TEXT, 
	expense_date DATETIME, 
	period_start DATETIME, 
	period_end DATETIME, 
	usage_details JSON, 
	invoice_url VARCHAR(500), 
	status VARCHAR(50), 
	is_recurring BOOLEAN, 
	recurring_period VARCHAR(50), 
	created_at DATETIME, 
	created_by_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(service_provider_id) REFERENCES service_providers (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
CREATE TABLE project_revisions (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	revision_number INTEGER NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT NOT NULL, 
	status VARCHAR(50), 
	priority VARCHAR(20), 
	created_by_id INTEGER NOT NULL, 
	assigned_to_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	completed_at DATETIME, 
	estimated_time INTEGER, 
	actual_time INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by_id) REFERENCES users (id), 
	FOREIGN KEY(assigned_to_id) REFERENCES admin_users (id)
);
CREATE TABLE revision_messages (
	id INTEGER NOT NULL, 
	revision_id INTEGER NOT NULL, 
	sender_type VARCHAR(20) NOT NULL, 
	sender_user_id INTEGER, 
	sender_admin_id INTEGER, 
	message TEXT NOT NULL, 
	is_internal BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(revision_id) REFERENCES project_revisions (id), 
	FOREIGN KEY(sender_user_id) REFERENCES users (id), 
	FOREIGN KEY(sender_admin_id) REFERENCES admin_users (id)
);
CREATE TABLE revision_files (
	id INTEGER NOT NULL, 
	revision_id INTEGER NOT NULL, 
	filename VARCHAR(500) NOT NULL, 
	original_filename VARCHAR(500) NOT NULL, 
	file_type VARCHAR(100) NOT NULL, 
	file_size INTEGER NOT NULL, 
	file_path VARCHAR(1000) NOT NULL, 
	uploaded_by_type VARCHAR(20) NOT NULL, 
	uploaded_by_user_id INTEGER, 
	uploaded_by_admin_id INTEGER, 
	description TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(revision_id) REFERENCES project_revisions (id), 
	FOREIGN KEY(uploaded_by_user_id) REFERENCES users (id), 
	FOREIGN KEY(uploaded_by_admin_id) REFERENCES admin_users (id)
);
CREATE TABLE revision_message_files (
	id INTEGER NOT NULL, 
	message_id INTEGER NOT NULL, 
	filename VARCHAR(500) NOT NULL, 
	original_filename VARCHAR(500) NOT NULL, 
	file_type VARCHAR(100) NOT NULL, 
	file_size INTEGER NOT NULL, 
	file_path VARCHAR(1000) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(message_id) REFERENCES revision_messages (id)
);
INSERT INTO revision_message_files VALUES(1,5,'e539ea8b57df40e0b355108a3feb6a51.file','image_1','image',233174,'uploads/revisions/bot/revision_10/e539ea8b57df40e0b355108a3feb6a51.file','2025-07-17 13:39:37.523635');
INSERT INTO revision_message_files VALUES(2,10,'94a08969-d6a1-4e85-870a-78a4c35f5e78.jpg','test_image.jpg','image',18,'uploads/revisions/messages/94a08969-d6a1-4e85-870a-78a4c35f5e78.jpg','2025-07-17 20:46:07.715816');
INSERT INTO revision_message_files VALUES(3,11,'f7d2ece5-2d73-423e-8ba3-03265e942d5e.jpg','до.jpg','image',453341,'uploads/revisions/messages/f7d2ece5-2d73-423e-8ba3-03265e942d5e.jpg','2025-07-17 20:48:17.782597');
INSERT INTO revision_message_files VALUES(4,12,'f318027d-72a3-4f30-95be-06c780a5a84d.jpg','после (1).jpg','image',403802,'uploads/revisions/messages/f318027d-72a3-4f30-95be-06c780a5a84d.jpg','2025-07-17 20:48:41.671472');
INSERT INTO revision_message_files VALUES(5,13,'3eb6dc36-6e77-4f18-8571-1f883ee0a06d.png','test_chat_image.png','image',584,'uploads/revisions/messages/3eb6dc36-6e77-4f18-8571-1f883ee0a06d.png','2025-07-17 20:56:07.659132');
INSERT INTO revision_message_files VALUES(6,14,'93bfd02b-9e91-4137-9a6b-8b582ee03e79.jpg','после.jpg','image',403802,'uploads/revisions/messages/93bfd02b-9e91-4137-9a6b-8b582ee03e79.jpg','2025-07-17 20:57:23.901126');
INSERT INTO revision_message_files VALUES(7,15,'fa5632fa-7bb7-492f-9077-731fa2060a8b.jpg','после (1).jpg','image',403802,'uploads/revisions/messages/fa5632fa-7bb7-492f-9077-731fa2060a8b.jpg','2025-07-17 21:11:06.198829');
INSERT INTO revision_message_files VALUES(8,16,'345c7571d26540f1a76c0b6c9d081e4d.jpg','photo.jpg','image',84383,'uploads/revisions/bot/revision_12/345c7571d26540f1a76c0b6c9d081e4d.jpg','2025-07-17 22:19:05.678886');
INSERT INTO revision_message_files VALUES(9,16,'70ca46ad7cb243f1983b1ddbd026a8a9.jpg','photo.jpg','image',145523,'uploads/revisions/bot/revision_12/70ca46ad7cb243f1983b1ddbd026a8a9.jpg','2025-07-17 22:19:05.678889');
INSERT INTO revision_message_files VALUES(10,16,'e0af082e9c9b4d4d9f34c10a76190111.jpg','photo.jpg','image',153279,'uploads/revisions/bot/revision_12/e0af082e9c9b4d4d9f34c10a76190111.jpg','2025-07-17 22:19:05.678890');
INSERT INTO revision_message_files VALUES(11,16,'ae6bd50cad454bd7807415ec25e8056a.jpg','photo.jpg','image',177290,'uploads/revisions/bot/revision_12/ae6bd50cad454bd7807415ec25e8056a.jpg','2025-07-17 22:19:05.678891');
INSERT INTO revision_message_files VALUES(12,1,'3acb09f2f4f94ba19d4a5a2c4b87b518.jpg','photo.jpg','image',145523,'uploads/revisions/bot/revision_1/3acb09f2f4f94ba19d4a5a2c4b87b518.jpg','2025-07-19 13:18:25.955184');
INSERT INTO revision_message_files VALUES(13,2,'912232da-7b74-4bc4-b7b0-399067696d1c.jpg','121212.jpg','image',83109,'uploads/revisions/messages/912232da-7b74-4bc4-b7b0-399067696d1c.jpg','2025-07-20 21:33:31.577259');
INSERT INTO revision_message_files VALUES(14,3,'e065b89eded2491489137ac92e45416c.jpg','photo.jpg','image',52786,'uploads/revisions/bot/revision_2/e065b89eded2491489137ac92e45416c.jpg','2025-07-21 20:21:14.581024');
INSERT INTO revision_message_files VALUES(15,1,'b3e7b451-ff99-432b-b24c-7f3f7bb1971b.png','ChatGPT Image 1 авг. 2025 г., 13_22_06.png','image',946515,'uploads/revisions/messages/b3e7b451-ff99-432b-b24c-7f3f7bb1971b.png','2025-08-01 21:39:31.365019');
INSERT INTO revision_message_files VALUES(16,2,'13547171-f6d9-4741-aba6-a154f8a1880d.png','ChatGPT Image 1 авг. 2025 г., 13_22_06.png','image',946515,'uploads/revisions/messages/13547171-f6d9-4741-aba6-a154f8a1880d.png','2025-08-01 21:58:34.362891');
INSERT INTO revision_message_files VALUES(17,3,'f9a9477f-ac46-4eac-9dcf-092788666d51.png','ChatGPT Image 1 авг. 2025 г., 13_22_06.png','image',946515,'uploads/revisions/messages/f9a9477f-ac46-4eac-9dcf-092788666d51.png','2025-08-01 21:59:12.154086');
INSERT INTO revision_message_files VALUES(18,4,'48476875c060440b8461215713da4137.jpg','photo.jpg','image',68223,'uploads/revisions/bot/revision_4/48476875c060440b8461215713da4137.jpg','2025-08-02 13:50:33.955689');
CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
                    assigned_to_id INTEGER NOT NULL,
                    created_by_id INTEGER NOT NULL,
                    deadline DATETIME,
                    estimated_hours INTEGER,
                    actual_hours INTEGER,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    task_metadata JSON DEFAULT '{}', color VARCHAR(20) DEFAULT 'normal',
                    FOREIGN KEY (assigned_to_id) REFERENCES admin_users (id),
                    FOREIGN KEY (created_by_id) REFERENCES admin_users (id)
                );
INSERT INTO tasks VALUES(33,'Бот для бронирования поставок НОВЫЙ','Паше изучить бота из ТЗ и переделать бота под клиента ','in_progress','normal',5,1,'2025-07-26 08:56:00.000000',10,NULL,'2025-07-23 05:56:38.650976','2025-08-04 09:47:03.888734',NULL,'{}','red');
INSERT INTO tasks VALUES(39,'БОТ Автосервис','Бот автосервис доделать интеграцию с Yclients и сдать клиенту также проверить все функции перед загрузкой на сервер','pending','high',5,1,'2025-07-26 09:07:00.000000',5,NULL,'2025-07-23 06:07:22.619995','2025-07-23 06:07:22.620003',NULL,'{}','yellow');
INSERT INTO tasks VALUES(46,'LT Coin бот по внутренней криптовалюте компании','Доделать стакан (P2P) проверить весь функционал бота прикрутить оплату и убрать полностью реферальную систему потом перенести на сервер','pending','high',5,1,'2025-07-31 09:28:00.000000',10,NULL,'2025-07-23 06:28:38.717007','2025-07-23 06:28:38.717025',NULL,'{}','yellow');
INSERT INTO tasks VALUES(47,'Роман - бот по Wildberries логистика','Доделать бота по вб для Романа ( удержания и сдать проект перенести на сервер) перед сдачей проверить работоспособность бота','in_progress','normal',2,1,'2025-07-24 09:30:00.000000',1,NULL,'2025-07-23 06:30:09.768226','2025-07-28 06:19:36.578102','2025-07-28 06:19:29.557961','{}','green');
INSERT INTO tasks VALUES(48,'Приложние одежда МиниАпп ','Приступить к выполнению задачи миниапп согласно ТЗ и сдать его до конца августа учитывать сроки ( тут работаем до договору) Я скину наработки по данному приложению','pending','low',4,1,'2025-08-31 09:33:00.000000',30,NULL,'2025-07-23 06:33:43.185779','2025-08-04 09:46:50.459209',NULL,'{}','green');
INSERT INTO tasks VALUES(50,'Приложение Мини Апп Лига Климата','Доделать приложение миниапп лига климата ( не горит) подправить дизайн возможно что то где то поменять согласуем на созвоне ( не горит)','pending','low',4,1,'2025-09-06 09:37:00.000000',20,NULL,'2025-07-23 06:37:25.628844','2025-08-04 09:46:44.632254',NULL,'{}','green');
INSERT INTO tasks VALUES(56,'Бот Ai Consultant ','Бот Ai Consultant начать внедрение генерации основных документов ','pending','normal',3,1,'2025-07-31 09:17:00.000000',20,NULL,'2025-07-28 06:17:11.439897','2025-07-28 06:17:11.439901',NULL,'{}','normal');
INSERT INTO tasks VALUES(58,'Бот Секта ','приступить к выполнению бота согласно ТЗ ','pending','high',3,1,'2025-08-10 12:11:00.000000',10,NULL,'2025-08-04 09:12:18.315426','2025-08-04 09:12:18.315439',NULL,'{}','green');
INSERT INTO tasks VALUES(59,'Бот парсер новостей CryptoPanic','выполнить задачу по парсингу новостей сайта криптопаник в телеграм и переводить новости на русский язык','pending','normal',7,1,'2025-08-08 12:17:00.000000',10,NULL,'2025-08-04 09:17:15.353001','2025-08-04 09:17:15.353011',NULL,'{}','green');
INSERT INTO tasks VALUES(60,'Бот по продаже чехлов для руля ',replace(replace('+7 985 911 9505 ждем начала следующей недели чтоы приступить к боту\r\n','\r',char(13)),'\n',char(10)),'pending','normal',1,1,'2025-08-11 12:40:00.000000',20,NULL,'2025-08-04 09:40:52.571110','2025-08-04 09:40:52.571123',NULL,'{}','green');
INSERT INTO tasks VALUES(61,'Таблица умножения Мини Апп',replace(replace('перенести приложение на сервер \r\n\r\n+79152221425. Tatu150489! - юкасса\r\n\r\n\r\nfp93468  Tatu150489! таймбев\r\n\r\n\r\nbagetstroy@gmail.com.  z_nFNyP8 рег ру','\r',char(13)),'\n',char(10)),'pending','low',4,1,'2025-08-06 12:45:00.000000',3,NULL,'2025-08-04 09:45:30.978687','2025-08-04 09:45:30.978696',NULL,'{}','green');
INSERT INTO tasks VALUES(62,'Мини апп планировщик проектов приступить','Отправить мне варианты дизайна мини аппа и согласовать диазйн с клиентом','pending','normal',4,1,'2025-08-06 12:46:00.000000',10,NULL,'2025-08-04 09:46:38.086827','2025-08-04 09:46:38.086837',NULL,'{}','green');
INSERT INTO tasks VALUES(63,'@alisakolmaer связаться 6 августа по решению','бот для коммуникации исполнптелей и подрядчиков','pending','normal',1,1,'2025-08-06 12:48:00.000000',1,NULL,'2025-08-04 09:48:31.804844','2025-08-04 09:48:31.804853',NULL,'{}','green');
INSERT INTO tasks VALUES(64,'оплата первая часть за бот аи консультант','оплата в юсдт ','pending','high',1,1,'2025-08-04 12:50:00.000000',1,NULL,'2025-08-04 09:50:37.776769','2025-08-04 09:50:37.776775',NULL,'{}','green');
INSERT INTO tasks VALUES(65,'Автоматизация рассылки ТГ',replace(replace('89315532633 н7ужно изучить рассылки в телеграме почему блокируют и насколько долго проживает телеграм премиум \r\n\r\nнадо сделать бота который будет парсить участников группы канала в телеграме и выгружать их в базу потом к этому боту подключаем 10 -15 аккаунтов с тг премиумом и надо писать в личку и выводить человека на диалог \r\n\r\nсамое главное обойти блокировки телеграма (изучить) также нужно выкатить человеку стоимоть решения и сроки а также попытаться рассчитать его расходы на данную задачу в круг \r\n\r\nсвязаться в течение пары дней ','\r',char(13)),'\n',char(10)),'pending','normal',1,1,'2025-08-06 15:05:00.000000',10,NULL,'2025-08-04 12:05:35.901048','2025-08-04 12:05:35.901056',NULL,'{}','green');
INSERT INTO tasks VALUES(66,'@lisa_const',replace(replace('заказчику нужен бот с интеграцией для срм системы Alfa CRM для сбора статистики \r\n\r\nсвязаться до 6 августа для уточнения сделки ','\r',char(13)),'\n',char(10)),'pending','normal',1,1,'2025-08-06 16:42:00.000000',1,NULL,'2025-08-04 13:42:10.961023','2025-08-04 13:42:10.961030',NULL,'{}','normal');
INSERT INTO tasks VALUES(67,'Бот для автосервиса диагностика шаги','связаться 5 августа клиент по имени на связи','pending','normal',1,1,'2025-08-05 21:12:00.000000',1,NULL,'2025-08-04 18:13:03.116008','2025-08-04 18:13:03.116012',NULL,'{}','green');
INSERT INTO tasks VALUES(68,'Приложение мебель в аренду',replace(replace('нужно составить комплексное техническое задание + коммерческое предложение по ТЗ клиента ( с начала реализуем не весь функционал без AR)\r\n\r\nнадо прописать сроки цену и затраты на всех этапах для клиента ','\r',char(13)),'\n',char(10)),'completed','urgent',1,1,'2025-08-05 23:42:00.000000',2,NULL,'2025-08-04 20:42:53.233995','2025-08-05 11:51:00.195789','2025-08-05 11:51:00.195763','{}','green');
CREATE TABLE task_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    comment_type VARCHAR(50) NOT NULL DEFAULT 'general',
                    is_internal BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (author_id) REFERENCES admin_users (id)
                );
INSERT INTO task_comments VALUES(19,47,1,'Изменения: статус: pending → completed','status_change',0,'2025-07-28 06:18:58.326361');
INSERT INTO task_comments VALUES(20,47,1,'Бот готов ожидает оплаты!','general',0,'2025-07-28 06:19:12.603657');
INSERT INTO task_comments VALUES(21,47,1,'Изменения: статус: completed → in_progress','status_change',0,'2025-07-28 06:19:23.328101');
INSERT INTO task_comments VALUES(22,47,1,'Изменения: статус: in_progress → completed','status_change',0,'2025-07-28 06:19:29.559714');
INSERT INTO task_comments VALUES(23,47,1,'Изменения: статус: completed → in_progress','status_change',0,'2025-07-28 06:19:35.161075');
INSERT INTO task_comments VALUES(24,47,1,'Изменения: цвет: yellow → green','status_change',0,'2025-07-28 06:19:36.579532');
INSERT INTO task_comments VALUES(25,50,1,'Изменения: цвет: normal → green','status_change',0,'2025-08-04 09:46:44.636696');
INSERT INTO task_comments VALUES(26,48,1,'Изменения: цвет: normal → green','status_change',0,'2025-08-04 09:46:50.469907');
INSERT INTO task_comments VALUES(27,33,1,'Изменения: статус: pending → in_progress','status_change',0,'2025-08-04 09:47:00.616215');
INSERT INTO task_comments VALUES(28,33,1,'Изменения: цвет: normal → red','status_change',0,'2025-08-04 09:47:03.892400');
INSERT INTO task_comments VALUES(29,68,1,'Изменения: статус: pending → completed','status_change',0,'2025-08-05 11:51:00.202626');
CREATE TABLE money_transactions (
	id INTEGER NOT NULL, 
	amount FLOAT NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	description TEXT, 
	date DATETIME NOT NULL, 
	receipt_file_path VARCHAR(500), 
	ocr_data JSON, 
	is_ocr_processed BOOLEAN, 
	notes TEXT, 
	source VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	created_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO money_transactions VALUES(1,25000.0,'income','Прочие доходы','Транзакция из чека receipt_501613334_1754255974.jpg','2025-08-03 00:00:00.000000','uploads/receipts/receipt_501613334_1754255974.jpg','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": \"25000\",\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1,NULL,'ocr','2025-08-03 21:19:45.163444','2025-08-03 21:19:45.163450',1);
INSERT INTO money_transactions VALUES(2,25000.0,'income','Прочие доходы','Транзакция из чека receipt_501613334_1754256918.jpg','2025-08-03 00:00:00.000000','uploads/receipts/receipt_501613334_1754256918.jpg','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1,NULL,'ocr','2025-08-03 21:35:24.011495','2025-08-03 21:35:24.011500',1);
CREATE TABLE money_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	description TEXT, 
	color VARCHAR(7), 
	icon VARCHAR(50), 
	is_active BOOLEAN, 
	sort_order INTEGER, 
	created_at DATETIME, 
	created_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO money_categories VALUES(1,'Разработка ботов','income',NULL,'#28a745','fas fa-robot',1,1,'2025-08-03 13:36:21.779103',1);
INSERT INTO money_categories VALUES(2,'Веб-разработка','income',NULL,'#007bff','fas fa-code',1,2,'2025-08-03 13:36:21.779110',1);
INSERT INTO money_categories VALUES(3,'Консультации','income',NULL,'#17a2b8','fas fa-handshake',1,3,'2025-08-03 13:36:21.779110',1);
INSERT INTO money_categories VALUES(4,'Интеграции','income',NULL,'#6610f2','fas fa-plug',1,4,'2025-08-03 13:36:21.779111',1);
INSERT INTO money_categories VALUES(5,'Поддержка','income',NULL,'#fd7e14','fas fa-tools',1,5,'2025-08-03 13:36:21.779112',1);
INSERT INTO money_categories VALUES(6,'Обучение','income',NULL,'#20c997','fas fa-graduation-cap',1,6,'2025-08-03 13:36:21.779112',1);
INSERT INTO money_categories VALUES(7,'Прочие доходы','income',NULL,'#6c757d','fas fa-plus-circle',1,99,'2025-08-03 13:36:21.779113',1);
INSERT INTO money_categories VALUES(8,'Еда','expense',NULL,'#dc3545','fas fa-utensils',1,1,'2025-08-03 13:36:21.779113',1);
INSERT INTO money_categories VALUES(9,'Транспорт','expense',NULL,'#ffc107','fas fa-car',1,2,'2025-08-03 13:36:21.779114',1);
INSERT INTO money_categories VALUES(10,'Жилье','expense',NULL,'#8B4513','fas fa-home',1,3,'2025-08-03 13:36:21.779114',1);
INSERT INTO money_categories VALUES(11,'Коммунальные услуги','expense',NULL,'#6f42c1','fas fa-bolt',1,4,'2025-08-03 13:36:21.779114',1);
INSERT INTO money_categories VALUES(12,'Интернет','expense',NULL,'#0dcaf0','fas fa-wifi',1,5,'2025-08-03 13:36:21.779115',1);
INSERT INTO money_categories VALUES(13,'Софт и подписки','expense',NULL,'#6610f2','fas fa-laptop',1,6,'2025-08-03 13:36:21.779115',1);
INSERT INTO money_categories VALUES(14,'Хостинг','expense',NULL,'#198754','fas fa-server',1,7,'2025-08-03 13:36:21.779116',1);
INSERT INTO money_categories VALUES(15,'Реклама','expense',NULL,'#fd7e14','fas fa-bullhorn',1,8,'2025-08-03 13:36:21.779116',1);
INSERT INTO money_categories VALUES(16,'Образование','expense',NULL,'#20c997','fas fa-book',1,9,'2025-08-03 13:36:21.779117',1);
INSERT INTO money_categories VALUES(17,'Здоровье','expense',NULL,'#dc3545','fas fa-heartbeat',1,10,'2025-08-03 13:36:21.779117',1);
INSERT INTO money_categories VALUES(18,'Развлечения','expense',NULL,'#e83e8c','fas fa-gamepad',1,11,'2025-08-03 13:36:21.779118',1);
INSERT INTO money_categories VALUES(19,'Одежда','expense',NULL,'#795548','fas fa-tshirt',1,12,'2025-08-03 13:36:21.779118',1);
INSERT INTO money_categories VALUES(20,'Налоги','expense',NULL,'#343a40','fas fa-file-invoice-dollar',1,13,'2025-08-03 13:36:21.779119',1);
INSERT INTO money_categories VALUES(21,'Прочие расходы','expense',NULL,'#6c757d','fas fa-minus-circle',1,99,'2025-08-03 13:36:21.779119',1);
CREATE TABLE receipt_files (
	id INTEGER NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	original_filename VARCHAR(255) NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	file_size INTEGER NOT NULL, 
	file_type VARCHAR(50) NOT NULL, 
	ocr_status VARCHAR(50), 
	ocr_result JSON, 
	ocr_confidence FLOAT, 
	ocr_error TEXT, 
	transaction_id INTEGER, 
	uploaded_at DATETIME, 
	processed_at DATETIME, 
	uploaded_by_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(transaction_id) REFERENCES money_transactions (id), 
	FOREIGN KEY(uploaded_by_id) REFERENCES admin_users (id)
);
INSERT INTO receipt_files VALUES(1,'receipt_501613334_1754254464.jpg','receipt_501613334_1754254464.jpg','uploads/receipts/receipt_501613334_1754254464.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.2999999999999999889,NULL,NULL,'2025-08-03 20:54:25.665755','2025-08-03 20:54:25.664995',1);
INSERT INTO receipt_files VALUES(2,'receipt_501613334_1754254767.jpg','receipt_501613334_1754254767.jpg','uploads/receipts/receipt_501613334_1754254767.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.2999999999999999889,NULL,NULL,'2025-08-03 20:59:28.490495','2025-08-03 20:59:28.490233',1);
INSERT INTO receipt_files VALUES(3,'receipt_501613334_1754255123.jpg','receipt_501613334_1754255123.jpg','uploads/receipts/receipt_501613334_1754255123.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.2999999999999999889,NULL,NULL,'2025-08-03 21:05:24.503022','2025-08-03 21:05:24.502330',1);
INSERT INTO receipt_files VALUES(4,'receipt_501613334_1754255458.jpg','receipt_501613334_1754255458.jpg','uploads/receipts/receipt_501613334_1754255458.jpg',59737,'jpg','failed','{"success": false, "error": "AI API \u043e\u0448\u0438\u0431\u043a\u0430: 401", "confidence": 0.0}',0.0,'AI API ошибка: 401',NULL,'2025-08-03 21:11:00.323678','2025-08-03 21:11:00.321328',1);
INSERT INTO receipt_files VALUES(5,'receipt_501613334_1754255616.jpg','receipt_501613334_1754255616.jpg','uploads/receipts/receipt_501613334_1754255616.jpg',61063,'jpg','failed','{"success": false, "error": "AI API \u043e\u0448\u0438\u0431\u043a\u0430: 401", "confidence": 0.0}',0.0,'AI API ошибка: 401',NULL,'2025-08-03 21:13:37.774888','2025-08-03 21:13:37.772337',1);
INSERT INTO receipt_files VALUES(6,'receipt_501613334_1754255749.jpg','receipt_501613334_1754255749.jpg','uploads/receipts/receipt_501613334_1754255749.jpg',60940,'jpg','failed','{"success": false, "error": "AI API \u043e\u0448\u0438\u0431\u043a\u0430: 401", "confidence": 0.0}',0.0,'AI API ошибка: 401',NULL,'2025-08-03 21:15:51.048429','2025-08-03 21:15:51.046924',1);
INSERT INTO receipt_files VALUES(7,'receipt_501613334_1754255974.jpg','receipt_501613334_1754255974.jpg','uploads/receipts/receipt_501613334_1754255974.jpg',60862,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": \"25000\",\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 21:19:37.922493','2025-08-03 21:19:37.920676',1);
INSERT INTO receipt_files VALUES(8,'receipt_501613334_1754256918.jpg','receipt_501613334_1754256918.jpg','uploads/receipts/receipt_501613334_1754256918.jpg',59737,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 21:35:21.769523','2025-08-03 21:35:21.768867',1);
INSERT INTO receipt_files VALUES(9,'receipt_501613334_1754257769.jpg','receipt_501613334_1754257769.jpg','uploads/receipts/receipt_501613334_1754257769.jpg',61063,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 21:49:33.370281','2025-08-03 21:49:33.369587',1);
INSERT INTO receipt_files VALUES(10,'receipt_501613334_1754258312.jpg','receipt_501613334_1754258312.jpg','uploads/receipts/receipt_501613334_1754258312.jpg',60940,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 21:58:36.557189','2025-08-03 21:58:36.556602',1);
INSERT INTO receipt_files VALUES(11,'receipt_501613334_1754258664.jpg','receipt_501613334_1754258664.jpg','uploads/receipts/receipt_501613334_1754258664.jpg',59737,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 22:04:28.511672','2025-08-03 22:04:28.511432',1);
INSERT INTO receipt_files VALUES(12,'receipt_501613334_1754258679.jpg','receipt_501613334_1754258679.jpg','uploads/receipts/receipt_501613334_1754258679.jpg',59737,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-03 22:04:42.376986','2025-08-03 22:04:42.376390',1);
INSERT INTO receipt_files VALUES(13,'receipt_501613334_1754291781.jpg','receipt_501613334_1754291781.jpg','uploads/receipts/receipt_501613334_1754291781.jpg',59737,'jpg','completed','{"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-04 07:16:25.819094','2025-08-04 07:16:25.818244',1);
INSERT INTO receipt_files VALUES(14,'receipt_501613334_1754291804.jpg','receipt_501613334_1754291804.jpg','uploads/receipts/receipt_501613334_1754291804.jpg',64774,'jpg','completed','{"success": true, "amount": 10000.0, "date": "2025-07-30T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": \"10000\",\n    \"date\": \"30.07.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1.0\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-04 07:16:48.428819','2025-08-04 07:16:48.428605',1);
INSERT INTO receipt_files VALUES(15,'receipt_501613334_1754291831.jpg','receipt_501613334_1754291831.jpg','uploads/receipts/receipt_501613334_1754291831.jpg',64859,'jpg','completed','{"success": true, "amount": 80000.0, "date": "2025-08-01T00:00:00", "organization": "\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 80000,\n    \"date\": \"01.08.2025\",\n    \"organization\": \"\u043e\u0437\u043e\u043d \u0431\u0430\u043d\u043a\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-04 07:17:15.159222','2025-08-04 07:17:15.158598',1);
INSERT INTO receipt_files VALUES(16,'receipt_501613334_1754298071.jpg','receipt_501613334_1754298071.jpg','uploads/receipts/receipt_501613334_1754298071.jpg',62015,'jpg','completed','{"success": true, "amount": 5000.0, "date": "2025-08-04T00:00:00", "organization": "\u041e\u041e\u041e \"\u041a\u0415\u0425 \u042d\u041a\u041e\u041c\u041c\u0415\u0420\u0426\"", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 5000,\n    \"date\": \"04.08.2025\",\n    \"organization\": \"\u041e\u041e\u041e \\\"\u041a\u0415\u0425 \u042d\u041a\u041e\u041c\u041c\u0415\u0420\u0426\\\"\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',1.0,NULL,NULL,'2025-08-04 09:01:16.439565','2025-08-04 09:01:16.437485',1);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('tasks',68);
INSERT INTO sqlite_sequence VALUES('task_comments',29);
CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_telegram_id ON users (telegram_id);
CREATE INDEX ix_portfolio_id ON portfolio (id);
CREATE INDEX ix_reviews_id ON reviews (id);
CREATE INDEX ix_faq_id ON faq (id);
CREATE INDEX ix_settings_id ON settings (id);
CREATE INDEX ix_admin_users_id ON admin_users (id);
CREATE UNIQUE INDEX ix_admin_users_username ON admin_users (username);
CREATE INDEX ix_projects_id ON projects (id);
CREATE INDEX ix_consultant_sessions_id ON consultant_sessions (id);
CREATE INDEX ix_messages_id ON messages (id);
CREATE INDEX ix_consultant_queries_id ON consultant_queries (id);
CREATE INDEX ix_files_id ON files (id);
CREATE INDEX ix_project_files_id ON project_files (id);
CREATE INDEX ix_project_statuses_id ON project_statuses (id);
CREATE INDEX ix_project_status_logs_id ON project_status_logs (id);
CREATE INDEX ix_finance_categories_id ON finance_categories (id);
CREATE INDEX ix_finance_transactions_id ON finance_transactions (id);
CREATE INDEX ix_finance_budgets_id ON finance_budgets (id);
CREATE INDEX ix_contractors_id ON contractors (id);
CREATE INDEX ix_service_providers_id ON service_providers (id);
CREATE INDEX ix_finance_reports_id ON finance_reports (id);
CREATE INDEX ix_contractor_payments_id ON contractor_payments (id);
CREATE INDEX ix_service_expenses_id ON service_expenses (id);
CREATE INDEX ix_project_revisions_id ON project_revisions (id);
CREATE INDEX ix_revision_messages_id ON revision_messages (id);
CREATE INDEX ix_revision_files_id ON revision_files (id);
CREATE INDEX ix_revision_message_files_id ON revision_message_files (id);
CREATE INDEX idx_tasks_assigned_to ON tasks (assigned_to_id);
CREATE INDEX idx_tasks_created_by ON tasks (created_by_id);
CREATE INDEX idx_tasks_status ON tasks (status);
CREATE INDEX idx_tasks_priority ON tasks (priority);
CREATE INDEX idx_tasks_deadline ON tasks (deadline);
CREATE INDEX idx_task_comments_task ON task_comments (task_id);
CREATE INDEX idx_task_comments_author ON task_comments (author_id);
CREATE INDEX ix_money_transactions_id ON money_transactions (id);
CREATE INDEX ix_money_categories_id ON money_categories (id);
CREATE INDEX ix_receipt_files_id ON receipt_files (id);
COMMIT;
