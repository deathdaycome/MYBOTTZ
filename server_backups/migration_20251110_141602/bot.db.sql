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
INSERT INTO users VALUES(1,501613334,'laytraces','Lay Traces',NULL,NULL,NULL,'2025-07-08 09:50:25.373461','2025-11-10 10:46:00.534097','main_menu','{"bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(2,123456789,'testuser','Test','User',NULL,NULL,'2025-07-09 09:35:59.746500','2025-07-09 09:42:28.611510','main_menu','{"bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", "bot_token_added_at": "2025-07-16T10:30:00", "timeweb_credentials": {"login": "test@example.com", "password": "password123", "created_at": "2025-07-16T10:25:00"}}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(3,12345,'test_user','Тест',NULL,'+79123456789','test@example.com','2025-07-09 09:49:51.734705','2025-07-16 10:42:52.316823','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(4,55555,'test_api_user','Тест API',NULL,'+79123456789','test_api@example.com','2025-07-09 09:53:02.308440','2025-07-09 09:53:02.308445','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(5,392743569,'Marina_vSTART','Марина СТАРТ',NULL,NULL,NULL,'2025-07-16 12:47:53.429217','2025-07-16 12:47:53.433403','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(6,289644296,'Invnv','Natalya','Ivanisheva',NULL,NULL,'2025-07-16 15:47:24.381651','2025-07-16 15:56:00.333915','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(7,3,NULL,NULL,NULL,NULL,NULL,'2025-07-17 08:19:51.845109','2025-07-17 08:19:51.850501','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(8,123,'test_user','Test','User',NULL,NULL,'2025-07-17 08:23:25.397657','2025-07-17 08:23:25.398936','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(9,737068813,'lockinbaby','NNG',NULL,NULL,NULL,'2025-07-17 10:24:23.671590','2025-07-26 00:42:12.883113','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(10,'@truetechshop','','Yekemini','','-',NULL,'2025-07-19 10:38:34.940581','2025-07-19 10:38:34.940602','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(11,6898088562,'','акака','','',NULL,'2025-07-19 11:12:44.564761','2025-11-07 13:16:00.047776','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(12,5804228677,'truetechshop','True','Tech',NULL,NULL,'2025-07-20 13:47:11.244797','2025-07-20 13:47:11.249215','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(13,999842003,'Vitalii_001','Виталий',NULL,NULL,NULL,'2025-07-20 21:16:39.542087','2025-07-20 21:21:09.024241','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(14,6261590247,'ezgef','𓅻ࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩ 𓅻ࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩࣩ',NULL,NULL,NULL,'2025-07-20 21:19:13.081317','2025-07-20 21:19:30.068562','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(15,8086446670,NULL,'ijkoup','jmcdaid',NULL,NULL,'2025-07-21 22:07:54.924267','2025-07-21 22:07:54.930149','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(16,5111697699,NULL,'Геннадий','Николаев',NULL,NULL,'2025-07-22 10:22:09.242383','2025-10-25 19:36:57.774798','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(17,469979893,'Zueva_Larisa','Larisa','Zueva',NULL,NULL,'2025-07-22 11:16:16.135108','2025-07-22 12:17:11.657158','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(18,5147523936,NULL,'CEO',NULL,NULL,NULL,'2025-07-22 11:20:04.270349','2025-07-22 11:20:31.832720','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(19,1221313,'','какакак','','',NULL,'2025-07-24 09:16:23.061319','2025-07-24 09:16:23.061324','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(20,323233332,'','какака','','332',NULL,'2025-07-26 09:32:26.664487','2025-07-26 09:32:26.664504','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(21,12345678,'','Виктор','','+79877510702',NULL,'2025-07-28 06:23:17.406303','2025-07-28 06:23:17.406308','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(22,'','','Павел Ерлыков','','',NULL,'2025-07-29 08:57:58.984755','2025-07-29 08:57:58.984760','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(23,'-','','Валерия Журавлева','','‪+7 963 954‑61‑04‬',NULL,'2025-07-29 09:03:01.499011','2025-07-29 09:03:01.499016','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(24,12313123,'виктор','Виктор',NULL,'999392109399',NULL,'2025-08-11 06:35:21.452858','2025-08-11 06:35:21.457290','registered','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(25,'аука','акуа_1754950081','акуа','','',NULL,'2025-08-11 22:08:01.766698','2025-08-11 22:08:01.766703','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(26,541526894,'xfce0','xfce0',NULL,NULL,NULL,'2025-08-14 20:16:14.143725','2025-11-06 20:27:46.580908','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(27,8128787651,'samir_skad1','#самир',NULL,NULL,NULL,'2025-08-15 08:18:29.574633','2025-08-15 08:18:29.583109','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(28,'@AlekseyKoroloff','алексей_1755435919','Алексей','','-',NULL,'2025-08-17 13:05:19.852685','2025-08-17 13:05:19.852700','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(29,'@acqua_panna','victor_1755436343','Victor','','-',NULL,'2025-08-17 13:12:23.256431','2025-08-17 13:12:23.256445','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(30,7232049739,'kogoto4ES','💐 ⃝ ⃝ ⃝ ⃝💐👉1️⃣👈💐 ⃝ ⃝ ⃝ ⃝💐',NULL,NULL,NULL,'2025-08-18 08:06:23.119121','2025-08-18 08:06:27.828055','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(31,285817730,NULL,'Olga','Dvoretskaia',NULL,NULL,'2025-08-21 07:04:38.004472','2025-08-21 07:05:03.233649','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(32,'@Ami_Vibe','амели_1755851900','Амели','','-',NULL,'2025-08-22 08:38:20.971122','2025-08-22 08:38:20.971127','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(33,1462496414,'brezh04','Алексей',NULL,NULL,NULL,'2025-08-22 14:53:49.999121','2025-08-22 14:54:12.143246','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(34,1756742268,'тест_1756742268','Тест','',NULL,NULL,'2025-09-01 15:57:48.568187','2025-09-01 15:57:48.568191','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(35,1756886380,'кака_1756886380','кака','','ака',NULL,'2025-09-03 07:59:40.505469','2025-09-03 07:59:40.505473','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(36,1756893758,'-_1756893758','-','','‪+7 960 164‑58‑88‬',NULL,'2025-09-03 10:02:38.157513','2025-09-03 10:02:38.157521','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(37,1756895015,'is_1756895015','IS','','‪+7 960 164‑58‑88‬',NULL,'2025-09-03 10:23:36.034839','2025-09-03 10:23:36.034844','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(38,1757568197,'roll_apple_1757568197','Roll APPLE','','-',NULL,'2025-09-11 05:23:17.348326','2025-09-11 05:23:17.348331','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(39,1757568462,'арсен_1757568462','Арсен','','-',NULL,'2025-09-11 05:27:42.931989','2025-09-11 05:27:42.931995','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(40,1758294626,'захар_1758294626','Захар','','‪+7 950 335‑02‑65‬',NULL,'2025-09-19 15:10:26.231202','2025-09-19 15:10:26.231206','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(41,1758294848,'-_1758294848','-','','‪+79135843011‬',NULL,'2025-09-19 15:14:08.948600','2025-09-19 15:14:08.948627','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(42,1758295361,'захар_востап_1758295361','Захар Востап','','‪+7 913 606‑20‑01‬',NULL,'2025-09-19 15:22:41.875063','2025-09-19 15:22:41.875068','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(43,1759226143,'надежда_1759226143','Надежда','','+46767119487',NULL,'2025-09-30 09:55:43.115943','2025-09-30 09:55:43.115946','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(44,1759226483,'вадим_1759226483','Вадим','','+79169497709',NULL,'2025-09-30 10:01:23.246094','2025-09-30 10:01:23.246098','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(45,1760122102,'егор_1760122102','Егор','','-',NULL,'2025-10-10 18:48:22.311728','2025-10-10 18:48:22.311737','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(46,1760122210,'вячеслав_1760122210','Вячеслав','','',NULL,'2025-10-10 18:50:10.295917','2025-10-10 18:50:10.295926','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(47,1760122416,'фарит_1760122416','Фарит','','-',NULL,'2025-10-10 18:53:36.790496','2025-10-10 18:53:36.790509','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(48,1760122605,'константин_1760122605','Константин','','',NULL,'2025-10-10 18:56:45.505234','2025-10-10 18:56:45.505246','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(49,1760122866,'-_1760122866','-','','‪+79266058800‬',NULL,'2025-10-10 19:01:06.398470','2025-10-10 19:01:06.398479','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(50,748499487,NULL,NULL,NULL,NULL,NULL,'2025-10-18 08:03:47.335922','2025-11-02 08:35:02.933359','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(51,391805684,'reg_queen','Regina',NULL,NULL,NULL,'2025-10-20 11:47:07.223189','2025-10-20 11:48:48.200169','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(52,717880688,'vbpsdkr','Егор',NULL,NULL,NULL,'2025-10-20 11:47:23.467516','2025-10-20 11:47:23.483035','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(53,547334994,'fo_support','F.O',NULL,NULL,NULL,'2025-10-20 14:44:49.231512','2025-10-25 13:01:06.896998','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(54,1363003331,'zv3zdochka','Oleg','Batsiev',NULL,NULL,'2025-10-21 11:36:12.029694','2025-10-21 11:41:54.497171','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(55,1761304232,'denis_k_1761304232','Denis K','','+79160074049',NULL,'2025-10-24 11:10:32.086008','2025-10-24 11:10:32.086013','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(56,1761306666,'николай_бот_доступ_к_группам_1761306666','Николай Бот доступ к группам','','+7 926 436 7178',NULL,'2025-10-24 11:51:06.961653','2025-10-24 11:51:06.961657','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(57,403053379,'Sdroal','Sdroal',NULL,NULL,NULL,'2025-10-24 11:54:58.962080','2025-10-24 17:27:47.166554','main_menu','{}',NULL,1,NULL,NULL,NULL,'403053379',NULL,0);
INSERT INTO users VALUES(58,449817818,'Aleksandr_Alekseevlch','Alexandr','',NULL,NULL,'2025-10-24 12:11:56.759759','2025-10-24 12:12:11.109496','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(59,8128520471,'q0e6q','01992292',NULL,NULL,NULL,'2025-10-24 15:26:37.033481','2025-11-10 10:46:56.023818','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(60,234263417,'DKvip11','Denis','К',NULL,NULL,'2025-10-24 18:30:36.285677','2025-11-04 07:36:08.486373','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(61,1762008199,'client_1762008199','Клиент','',NULL,NULL,'2025-11-01 14:43:19.997823','2025-11-01 14:43:19.997827','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(62,1762008211,'client_1762008211','Клиент','',NULL,NULL,'2025-11-01 14:43:31.646102','2025-11-01 14:43:31.646107','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(63,1762008230,'client_1762008230','Клиент','',NULL,NULL,'2025-11-01 14:43:50.752826','2025-11-01 14:43:50.752829','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(64,1762008620,'щшкра_1762008620','щшкра','',NULL,NULL,'2025-11-01 14:50:20.931440','2025-11-01 14:50:20.931444','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(65,1762009934,'кхащштукхащшу_1762009934','кхащштукхащшу','','уахщшкашщ',NULL,'2025-11-01 15:12:14.581137','2025-11-01 15:12:14.581140','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(66,999888777,'pythongodbless','PYTHONGODBLESS','Тестовый',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0);
INSERT INTO users VALUES(67,5138267356,NULL,NULL,NULL,NULL,NULL,'2025-11-06 15:07:46.212223','2025-11-06 16:46:38.486666','main_menu','{}',NULL,1,NULL,NULL,NULL,NULL,NULL,0);
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
	created_by INTEGER, is_published BOOLEAN DEFAULT 0, telegram_message_id INTEGER, published_at DATETIME, telegram_channel_id VARCHAR(100), 
	PRIMARY KEY (id)
);
INSERT INTO portfolio VALUES(1,'Бот для интернет-магазина',NULL,'Многофункциональный бот с каталогом товаров, корзиной, оплатой и уведомлениями о заказах','telegram_bot','telegram_bot_demo.jpg','[]','Python, Telegram Bot API, SQLite, Stripe API','medium',7,14,NULL,'35000-45000',0,NULL,NULL,'[]',1,1,1,1,0,NULL,NULL,'completed',NULL,'2025-07-08 09:38:12.505277','2025-07-20 07:03:02.134274',NULL,0,NULL,NULL,NULL);
INSERT INTO portfolio VALUES(2,'CRM-бот для управления клиентами',NULL,'Бот для автоматизации работы с клиентами, ведения базы данных и отправки рассылок','telegram_bot',NULL,'[]','Python, PostgreSQL, Redis, AmoCRM API','medium',8,21,NULL,'50000-70000',0,NULL,NULL,'[]',1,1,2,0,0,NULL,NULL,'completed',NULL,'2025-07-08 09:38:12.505282','2025-07-08 09:38:12.505283',NULL,0,NULL,NULL,NULL);
INSERT INTO portfolio VALUES(3,'Бот-опросник с аналитикой','','Интерактивный бот для проведения опросов с детальной аналитикой и экспортом результатов','telegram_bots',NULL,'[]','Python, Chart.js, Excel API, Google Sheets','medium',5,10,NULL,'',0,'','','[]',0,1,3,0,0,'','','completed',NULL,'2025-07-08 09:38:12.505285','2025-07-12 23:11:11.492716',NULL,0,NULL,NULL,NULL);
INSERT INTO portfolio VALUES(4,'оузукза','','кукаау','ai_integration',NULL,'[]','','medium',5,NULL,NULL,'',0,'','','[]',0,1,0,0,0,'','','completed',NULL,'2025-07-16 15:53:39.945715','2025-07-18 06:37:53.156628',NULL,0,NULL,NULL,NULL);
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
	last_login DATETIME, login_count INTEGER DEFAULT 0, failed_login_count INTEGER DEFAULT 0, last_failed_login DATETIME, is_locked BOOLEAN DEFAULT 0, locked_until DATETIME, password_changed_at DATETIME, must_change_password BOOLEAN DEFAULT 0, session_token VARCHAR(500), session_expires_at DATETIME, preferences JSON DEFAULT '{}', telegram_id BIGINT DEFAULT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO admin_users VALUES(1,'admin','cb872de2c8e7435bad0db5ce42b95b6e0ee8d27a8b1e0b9e10f5c1d9c8c4c8b6',NULL,'Администратор',NULL,'owner',1,NULL,NULL,0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',501613334);
INSERT INTO admin_users VALUES(3,'Casper123','da646f3cba48406c06a62ce9132bc92aa3b8b5ac6f41e2f8a26601d9f18d5169','kluchka619@gmail.com','Миша','Ключка','executor',1,'2025-07-20 21:31:48.856121','2025-11-04 11:55:05.005332',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',748499487);
INSERT INTO admin_users VALUES(4,'daniltechno','ee79976c9380d5e337fc1c095ece8c8f22f91f306ceeb161fa51fecede2c4ba1','hauslerreiner85@gmail.com','Даниил ','Михайлов','executor',1,'2025-07-23 05:31:02.673087','2025-11-06 17:30:27.381042',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',NULL);
INSERT INTO admin_users VALUES(5,'xfce0','ed34e117a4df253203b339bb0821f6b2836924e9ff8fdd52eb1bc2d07e44c91b','pavlinborisich@gmail.com','Павел','','executor',1,'2025-07-23 05:35:42.252919','2025-11-08 10:28:56.569538',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',541526894);
INSERT INTO admin_users VALUES(7,'gennic','c0c4a69b17a7955ac230bfc8db4a123eaa956ccf3c0022e68b8d4e2f5b699d1f','gennic@yandex.ru','Геннадий','Николаев','executor',1,'2025-08-03 10:02:35.247265',NULL,0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',5111697699);
INSERT INTO admin_users VALUES(8,'hyperpop','76c2226da3a0557d1713f229429848b612c05ee5d238b958a3d879b976c6f0a7','assparagus@icloud.com','Андрей','Карпов','executor',1,'2025-08-11 11:52:16.616650','2025-11-06 16:19:55.890088',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',8128520471);
INSERT INTO admin_users VALUES(9,'batsievoleg','15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225','mai.batsiev.oleg@gmail.com','Олег','Олег','executor',1,'2025-10-21 11:32:59.049639','2025-10-21 11:42:17.576498',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',1363003331);
INSERT INTO admin_users VALUES(10,'Inisei','15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225','initcframe@yahoo.com','Roman','Pogrebnyak','executor',1,'2025-10-29 08:56:58.531905','2025-11-02 10:47:57.815284',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',NULL);
INSERT INTO admin_users VALUES(11,'deathdaycome','5038194010abdce978a068450eaa22261ce3fc7aaf19cacb88c4ce8e6c16a5a3','-','Иван','Николаев','executor',1,'2025-11-02 10:47:47.782377','2025-11-02 16:01:36.213191',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',NULL);
INSERT INTO admin_users VALUES(12,'omen','ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f','piranik04@mail.ru','Никита ','Пирогов','executor',1,'2025-11-05 08:16:24.898679','2025-11-05 08:18:22.058538',0,0,NULL,0,NULL,NULL,0,NULL,NULL,'{}',NULL);
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
	assigned_at DATETIME, prepayment_amount REAL DEFAULT 0.0, client_paid_total REAL DEFAULT 0.0, executor_paid_total REAL DEFAULT 0.0, color VARCHAR(20) DEFAULT 'default', is_archived BOOLEAN DEFAULT 0, actual_end_date DATETIME, responsible_manager_id INTEGER, start_date DATETIME, planned_end_date DATETIME, source_deal_id INTEGER, paid_amount REAL DEFAULT 0.0, client_telegram_id VARCHAR(100), contract_document_id INTEGER, client_telegram_username VARCHAR(100), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(assigned_executor_id) REFERENCES admin_users (id)
);
INSERT INTO projects VALUES(1,10,'Бот TON / USDT',replace('Я хочу создать Telegram-бота с нуля, используя предоставленный мной API токен.\nБот должен:\n • Показывать приветственное сообщение и предлагать выбор категории:\nПодарочные карты, Устройства, Социальные услуги, VPN-ключи и SMS\n • Поддерживать два языка: английский и русский\n • Позволять пользователю выбрать бренд, регион (например, США, Великобритания) и номинал ($10, $25 и т.д.)\n • Отображать доступные способы оплаты: TON и USDT (TRC20)\n • Показывать адрес кошелька и, при выборе TON, давать ссылку на оплату через TON Wallet\n • Позволять загружать скриншот оплаты или указывать TXID\n • Автоматически уведомлять меня в Telegram с информацией о пользователе и подтверждением оплаты\n • (Опционально) Если возможно, бот может автоматически отправлять цифровой товар (например, код подарочной карты) после подтверждения\n • В противном случае — я буду выполнять заказы вручную после получения уведомления\n\nТакже прошу сообщить, какие инструменты или платформу вы планируете использовать для разработки (например, Manybot, Typebot или другое), чтобы я мог в будущем сам вносить правки при необходимости.','\n',char(10)),NULL,'{}','завершен','medium','bot','medium',80000.0,10000.0,NULL,40,NULL,'2025-07-23 13:31:00.000000','2025-07-19 10:38:34.941045','2025-10-18 17:08:03.990725','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-19T10:38:34.943289", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',4,'2025-10-18 17:08:03.990721',0.0,80000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(2,21,'БОТЫ Wildberries','Сделать 4 бота по Вайлдбериз для клиента',NULL,'{}','new','medium','bot','simple',145000.0,27999.999999999999999,NULL,15,NULL,'2025-07-31 09:23:00.000000','2025-07-28 06:23:17.406845','2025-09-03 08:01:36.214577','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-28T06:23:17.411871", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(3,22,'LTCoin - внутреняя криптовалюта компании',replace('Первый этап - делаем MVP\n📌 Минимальное техническое задание (MVP) для тестирования Telegram-бота LTcoin\nЦель проекта:\nСоздать максимально упрощённый Telegram-бот для тестирования интереса пользователей к виртуальной монете LTcoin компании «Лаборатория Творчества».\n\n⚙️ Минимальный функционал:\n1. Простая авторизация:\nАвторизация пользователя только через Telegram ID (без SMS-подтверждения).\n2. Личный кабинет (упрощённый):\nОтображает:\nБаланс пользователя (количество монет LTcoin).\nТекущую стоимость монет в рублях.\nПример интерфейса:\n👤 Личный кабинет LTcoin\n\n💰 Ваш баланс: 100 LTcoin\n📈 Текущая цена 1 LTcoin: 25 руб.\n📊 Общая стоимость: 2500 руб.\n3. Покупка монет (без интеграции платежей):\nПользователь отправляет заявку на покупку монет.\nАдминистратор вручную подтверждает оплату и начисляет монеты.\nФиксированная комиссия 1,95% (учёт вручную администратором).\n4. Возврат монет:\nПользователь подаёт заявку на возврат монет.\nАдминистратор вручную обрабатывает заявки, исходя из первоначальной стоимости покупки.\n5. Формирование стоимости монеты (упрощённо):\nАдминистратор вручную ежеквартально обновляет стоимость монеты на основе реальной прибыли компании.\nЦена монеты публикуется через простые уведомления в боте.\nПример:\n🔔 Новая стоимость LTcoin: 30 руб. за монету.\n\n📊 Управление (упрощённое):\nАдминистративные функции:\nРучное добавление и удаление монет пользователям.\nВручную обновлять цену монеты и информировать пользователей через сообщения в боте.\n\n🔐 Безопасность:\nМинимальный уровень безопасности через стандартную защиту Telegram (без сложной интеграции).\n\n🛠 Технические детали (минимальные):\nБаза данных:\nПростая SQLite-база данных для хранения данных пользователей и балансов.\nИнтеграция:\nТолько Telegram API без дополнительных сервисов.\n\n⚠️ Практические советы по реализации:\nМаксимально упростите пользовательский интерфейс.\nОперативно отвечайте на заявки пользователей вручную, чтобы протестировать спрос.\nИспользуйте готовые библиотеки и минимальное количество кастомного кода.\n\n📅 Сроки выполнения:\nРазработка базового функционала и простого личного кабинета: 5-7 дней.\nТестирование и запуск MVP: 1-2 дня.\n\n✅ Итоговый результат:\nМинимальный Telegram-бот, с простым личным кабинетом, возможностью ручной покупки и возврата монет, ручным обновлением стоимости и минимальными затратами времени и ресурсов для проверки спроса на LTcoin среди пользователей.','\n',char(10)),NULL,'{}','завершен','medium','bot','complex',129999.99999999999999,25999.999999999999999,NULL,50,NULL,'2025-08-03 11:57:00.000000','2025-07-29 08:57:58.990911','2025-09-29 06:54:26.914555','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T08:57:59.012065", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,150000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(4,23,'Бот характеристики ЯМ','Сделать бота который заполняет характеристики в шаблонах Яндекс Маркет использовать нейросеть DeepSeek',NULL,'{}','завершен','medium','bot','medium',35999.999999999999999,7199.9999999999999998,NULL,10,NULL,'2025-07-31 12:02:00.000000','2025-07-29 09:03:01.500072','2025-09-03 08:13:28.334760','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:03:01.512561", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(5,23,'Бот Детейлинг','Нужен бот для детейлинга с онлайн записью админ конслью и интеграцией Yclients',NULL,'{}','завершен','low','bot','medium',50000.0,10000.0,NULL,20,NULL,'2025-08-03 12:06:00.000000','2025-07-29 09:06:34.516984','2025-09-29 06:53:44.660552','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:06:34.539673", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,10000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(6,23,'Бот для бронирования поставок ( новый)','ТЗ у Паши в личных сообщениях сделать бота по примеру бронирование поставок перемещние товаров подписки и админ консоль',NULL,'{}','new','medium','bot','medium',75000.0,15000.0,NULL,20,NULL,'2025-08-01 12:10:00.000000','2025-07-29 09:10:46.264920','2025-09-03 08:13:45.842689','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:10:46.285172", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(7,23,'Mini App таблица умножения','ТЗ находится на сайте holst.com в личных сообщениях с заказчиком',NULL,'{}','new','high','app','complex',80000.0,20000.0,NULL,20,NULL,'2025-08-10 12:12:00.000000','2025-07-29 09:12:53.613044','2025-09-03 08:25:31.179084','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:12:53.633971", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,40000.0,0.0,'default',0,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(8,23,'Lunaria','ТЗ в личных сообщениях с заказчиком ( Даниил)',NULL,'{}','завершен','medium','app','medium',133149.99999999999999,30000.0,NULL,200,NULL,'2025-07-31 12:45:00.000000','2025-07-29 09:45:45.425095','2025-09-03 08:13:53.233922','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:45:45.440695", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(9,23,'Mini App одежда',replace('Техническое задание на разработку мини-приложения интернет-магазина\n1.⁠ ⁠Общее описание проекта\nРазработка мини-приложения (веб-приложения) для продажи одежды, обуви и аксессуаров с полным функционалом интернет-магазина, включая административную панель управления, интеграцию с платежной системой ЮKassa и системой аналитики.\n2.⁠ ⁠Функциональные требования\n2.1 Основной функционал интернет-магазина\n\nКаталог товаров с категориями (одежда, обувь, аксессуары)\nКарточки товаров с детальным описанием\nКорзина покупок\nСистема оформления заказов\nЛичный кабинет покупателя\nПоиск и фильтрация товаров\n\n2.2 Интеграция с платежной системой\n\nПодключение ЮKassa для приема платежей\nОбработка различных способов оплаты\nУведомления о статусе платежей\n\n2.3 Система управления контентом\n\nРедактор описаний товаров (1500-3000 символов)\nЗагрузка и управление изображениями товаров\nSEO-оптимизация карточек товаров\n\n2.4 Административная панель\n\nУправление товарами (добавление, редактирование, удаление)\nУправление ценами и скидками\nНастройка акций с временными ограничениями\nУправление заказами\n\n2.5 Аналитика и отчетность\n\nВоронка продаж\nСтатистика по магазину\nВыгрузка данных в Excel\nОтчеты по товарам и продажам\n\n2.6 Система уведомлений\n\nНапоминания о незавершенных покупках\nEmail/SMS уведомления\nPush-уведомления\n\n2.7 Маркетинговые инструменты\n\nСистема скидок и промокодов\nАкции с таймерами\nКарусель рекомендуемых товаров\n\n3.⁠ ⁠Этапы выполнения работ\nЭтап 1: Проектирование и планирование (5-7 дней)\nЗадачи:\n\nСоздание детального технического проекта\nПроектирование архитектуры системы\nСоздание схемы базы данных\nРазработка пользовательских сценариев (User Stories)\nСоздание wireframes и mockups интерфейсов\nПланирование интеграций\n\nРезультат: Утвержденный технический проект с макетами интерфейсов\nЭтап 2: Настройка инфраструктуры (3-4 дня)\nЗадачи:\n\nНастройка сервера и хостинга\nУстановка и настройка базы данных\nНастройка системы контроля версий\nСоздание среды разработки и тестирования\nНастройка SSL-сертификатов\n\nРезультат: Готовая инфраструктура для разработки\nЭтап 3: Backend разработка - Основа (8-10 дней)\nЗадачи:\n\nСоздание API для управления товарами\nРазработка системы пользователей и авторизации\nСоздание моделей данных (товары, заказы, пользователи)\nРеализация базовой логики магазина\nСоздание системы загрузки изображений\n\nРезультат: Функционирующий backend с базовым API\nЭтап 4: Frontend разработка - Пользовательский интерфейс (10-12 дней)\nЗадачи:\n\nСоздание главной страницы и каталога\nРазработка карточек товаров\nРеализация корзины покупок\nСоздание форм оформления заказа\nАдаптивная верстка для мобильных устройств\nРеализация поиска и фильтрации\n\nРезультат: Полноценный пользовательский интерфейс магазина\nЭтап 5: Интеграция с ЮKassa (4-5 дней)\nЗадачи:\n\nПодключение к API ЮKassa\nРеализация процесса оплаты\nОбработка webhooks для статусов платежей\nТестирование платежных сценариев\nОбработка ошибок и возвратов\n\nРезультат: Работающая система приема платежей\nЭтап 6: Административная панель (8-10 дней)\nЗадачи:\n\nСоздание интерфейса администратора\nСистема управления товарами\nРедактор описаний с ограничением символов\nУправление ценами и скидками\nСистема ролей и прав доступа\nЗагрузка и обработка изображений\n\nРезультат: Полнофункциональная административная панель\nЭтап 7: Система уведомлений (4-5 дней)\nЗадачи:\n\nНастройка email-рассылки\nРеализация напоминаний о корзине\nСоздание шаблонов уведомлений\nНастройка расписания отправки\nИнтеграция с SMS-сервисом (опционально)\n\nРезультат: Работающая система уведомлений\nЭтап 8: Маркетинговые инструменты (5-6 дней)\nЗадачи:\n\nСистема промокодов и скидок\nРеализация таймеров для акций\nКарусель рекомендованных товаров\nСистема персональных предложений\nНастройка автоматических скидок\n\nРезультат: Инструменты для проведения акций и скидок\nЭтап 9: Аналитика и отчетность (6-7 дней)\nЗадачи:\n\nСоздание системы сбора статистики\nРеализация воронки продаж\nСоздание дашборда с основными метриками\nРазработка системы экспорта в Excel\nНастройка автоматических отчетов\n\nРезультат: Система аналитики с возможностью экспорта данных\nЭтап 10: Тестирование и оптимизация (7-8 дней)\nЗадачи:\n\nФункциональное тестирование всех модулей\nТестирование производительности\nПроверка безопасности\nКроссбраузерное тестирование\nОптимизация скорости загрузки\nИсправление выявленных ошибок\n\nРезультат: Протестированное и оптимизированное приложение\nЭтап 11: Развертывание и запуск (3-4 дня)\nЗадачи:\n\nРазвертывание на продакшн-сервере\nНастройка мониторинга\nСоздание резервных копий\nФинальное тестирование в боевой среде\nОбучение администраторов\n\nРезультат: Запущенное в продакшн приложение\nЭтап 12: Документация и поддержка (2-3 дня)\nЗадачи:\n\nСоздание пользовательской документации\nНаписание технической документации\nПодготовка инструкций для администраторов\nНастройка системы мониторинга ошибок\n\nРезультат: Полная документация проекта\n4.⁠ ⁠Технические требования\n4.1 Backend\n\nЯзык программирования: Python (Django/FastAPI) или Node.js\nБаза данных: PostgreSQL\nСистема кэширования: Redis\nAPI: RESTful API\n\n4.2 Frontend\n\nФреймворк: React.js или Vue.js\nАдаптивный дизайн\nPWA возможности\n\n4.3 Интеграции\n\nЮKassa API для платежей\nEmail-сервис для уведомлений\nФайловое хранилище для изображений\n\n5.⁠ ⁠Общие сроки реализации\nОбщий срок разработки: 60-75 рабочих дней (12-15 недель)\n6.⁠ ⁠Критерии приемки\n\nВсе функции работают согласно техническому заданию\nПроведено полное тестирование\nПриложение оптимизировано для высокой производительности\nСозданы все необходимые отчеты и документация\nПроведено обучение пользователей','\n',char(10)),NULL,'{}','new','medium','app','medium',179999.99999999999999,30000.0,NULL,10,NULL,'2025-08-03 12:55:00.000000','2025-07-29 09:55:08.325587','2025-09-03 08:24:46.951370','{"created_manually": true, "created_by": "admin", "created_at": "2025-07-29T09:55:08.347041", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,90000.0,0.0,'default',0,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(11,23,'CRYPTOPANIC','Бот для выгрузки новостей по крипте в группу',NULL,'{}','завершен','medium','bot','medium',50000.0,10000.0,NULL,10,NULL,'2025-08-17 13:21:00.000000','2025-08-11 10:21:17.477865','2025-10-21 11:52:06.952841','{"status_history": [{"from_status": "new", "to_status": "\u043d\u0430_\u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "from_status_name": "\u041d\u043e\u0432\u044b\u0439", "to_status_name": "\u041d\u0430 \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438", "changed_at": "2025-09-03T08:15:54.011009", "comment": "", "changed_by": "admin"}]}',NULL,NULL,0.0,50000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(12,23,'Бот Кулинария (доступ в группу)',replace('по боту : \n\nбазовый бот : 10000\nинтеграция с платежками : 5000\nуведомления догонялки : 3500 рублей ( сюда входит личный кабинет человека + лк с подпиской)\n\nадминистратиная консоль расширенная ( отдельной страницей html) - 10000\n\nобщая стоиомсть - 28500','\n',char(10)),NULL,'{}','new','medium','bot','medium',28499.999999999999999,6000.0,NULL,2,NULL,'2025-08-15 00:00:00.000000','2025-08-12 07:40:09.130514','2025-09-03 08:14:05.589454','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-12T07:40:09.149921", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',3,NULL,14249.999999999999999,14249.999999999999999,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(13,23,'ПВЗ (учет соттрудников)','Бот должен вести учет смен сотрудников разных ПВЗ по примеру отправленному клиентом',NULL,'{}','завершен','medium','bot','medium',15000.0,6000.0,NULL,2,NULL,'2025-08-14 00:00:00.000000','2025-08-12 07:43:08.682178','2025-10-21 11:52:06.952845','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-12T07:43:08.688215", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',NULL,NULL,15000.0,30000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(14,23,'Интегрировать 4 системы оплаты в бота','клиент отправил код своего бота и попросил интегрировать 4 платежки в него',NULL,'{}','new','medium','bot','medium',13999.999999999999999,3000.0,NULL,2,NULL,'2025-08-17 00:00:00.000000','2025-08-12 07:45:46.786402','2025-09-03 08:14:37.770588','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-12T07:45:46.793105", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,12000.0,12000.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(15,23,'Автосервис ( диагностика ) Бот','по шаблону должен заполнять чек лист осмотра автомобиля и выдавать пдф файл',NULL,'{}','new','medium','bot','medium',35000.0,15000.0,NULL,40,NULL,'2025-08-14 00:00:00.000000','2025-08-12 07:52:39.667852','2025-09-03 08:14:48.225086','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-12T07:52:39.673687", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',1,NULL,17500.0,17500.0,0.0,'default',1,NULL,NULL,NULL,NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(16,23,'Парсер скидки WB','Бот должен парсить скидки и выгружать их в группу заказчика',NULL,'{}','accepted','medium','bot','medium',42500.0,8500.0,NULL,10,NULL,'2025-08-17 00:00:00.000000','2025-08-17 12:54:32.839944','2025-10-21 11:52:06.952846','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-17T12:54:32.856459", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',NULL,NULL,0.0,42500.0,8500.0,'default',1,NULL,NULL,'2025-08-17 12:54:32.847333',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(17,23,'ИИ консультант (Юридический)','выполнить бота помощника в юриспруднеции согласно тз от клиента',NULL,'{}','accepted','medium','website','medium',127499.99999999999999,NULL,NULL,0,NULL,'2025-08-24 00:00:00.000000','2025-08-17 12:56:39.723421','2025-10-20 18:49:03.868317','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-17T12:56:39.731760", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',3,NULL,60000.0,187500.0,15000.0,'default',1,NULL,NULL,'2025-08-17 12:56:39.727183',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(18,28,'Автобронирование WB (новый)','Авто бронирование ВБ новый бот нужно сделать по примеру того бота который отправил клиент техническое задание находится в чате с клиентом',NULL,'{}','new','medium','bot','medium',70000.0,13999.999999999999999,NULL,30,NULL,'2025-08-18 00:00:00.000000','2025-08-17 13:05:19.855194','2025-09-03 08:15:08.500758','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-17T13:05:19.861958", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,35000.0,35000.0,0.0,'default',1,NULL,NULL,'2025-08-17 13:05:19.856531',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(19,29,'Mini App "Прогресс проекты"',replace('📋 Техническое задание: Разработка Web-приложения “Mini APP”\n\n1. 📌 Описание проекта\n\nРазработать веб-приложение “Mimi APP”, целью которого является автоматизация расчётов и визуализация воронки продаж для пользователя на основе заданных целей по доходу и параметров проектов.\n\nПользователь проходит несколько шагов, вводит личные данные (например, желаемый годовой доход), указывает текущие показатели (например, процент от продаж), и приложение автоматически рассчитывает:\n • Сумму необходимой выручки\n • Необходимую воронку продаж\n • Распределение по проектам и задачам\n • Финансовые цели по каждому проекту\n\nПриложение должно помогать пользователю планировать и отслеживать прогресс.\n\n2. 🧩 Основной функционал\n\n2.1 Этап первый — Личные цели и метрики\n • Ввод пользовательских параметров:\n • Желаемый доход в год\n • Процент комиссии (от продаж)\n • Автоматический расчет:\n • Суммы продаж, необходимой для достижения цели\n • Необходимой воронки проектов (с учетом коэффициента конверсии)\n\n2.2 Этап второй — Проекты\n • Возможность добавлять проекты вручную:\n • Название проекта\n • Желаемая прибыль от проекта\n • Расчет:\n • Целей по каждому проекту\n • Суммарной выручки по проектам\n • Хранение карточек проектов\n\n2.3 Мини-ассистент (mini APP)\n • Отображение рекомендаций на каждом этапе\n • Интерактивные подсказки, встроенные в интерфейс\n\n3. ⚙️ Технические требования\n\n3.1 Архитектура и масштабируемость\n • Проект должен быть масштабируемым:\n • Возможность расширения количества этапов и метрик без глобальной переработки системы\n • Легкость интеграции дополнительных модулей (например, аналитики или интеграции с CRM)\n • Разделение фронтенда и бэкенда (например, с использованием REST API)\n\n3.2 Адаптивность\n • Интерфейс должен быть адаптивным:\n • Корректная работа на устройствах с разным разрешением (мобильные, планшеты, десктоп)\n • Использование фреймворков с адаптивной версткой (например, TailwindCSS, Bootstrap)\n\n3.3 Стек технологий (рекомендуемый)\n • Фронтенд: React / Vue / Angular\n • Бэкенд: Node.js / Python (Django/FastAPI)\n • База данных: PostgreSQL / MongoDB\n • Хостинг/инфраструктура: Docker + AWS / Vercel / Firebase\n • Возможность автономной работы с последующей синхронизацией (оффлайн-режим)\n\n4. 📊 Визуализация и интерфейс\n • Понятный и красивый UI дизайн\n • Графики/диаграммы по воронке и проектам\n • Возможность редактировать, сохранять и удалять данные\n • Интерфейс “пошагового помощника”\n\n5. 🔐 Безопасность и доступ\n • Авторизация (email + пароль / OAuth)\n • Хранение данных пользователя в изолированной среде\n • Шифрование чувствительной информации','\n',char(10)),NULL,'{}','accepted','low','other','medium',250000.0,85000.0,NULL,40,NULL,'2025-08-18 21:00:00.000000','2025-08-17 13:12:23.257814','2025-10-20 18:48:13.367228','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-17T13:12:23.265600", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',4,NULL,90000.0,250000.0,40000.0,'default',1,NULL,NULL,'2025-08-17 13:12:23.259482',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(20,32,'Бот Амели (учет финансы)',replace('Как устроить логику в боте\n1. Новый пользователь\nПриветствие (дружеское, лёгкое, как мы вчера обсуждали).\n«Тебе доступен бесплатный месяц. Веди расходы в 3 категориях и смотри, сколько можно тратить каждый день».\nКнопка «Начать».\n2. В течение бесплатного месяца\nУведомления: «Сегодня твой лимит — 1200₽. Потратил 750₽ — отлично! Остаток можно перенести на завтра».\nЛёгкая геймификация: «У тебя уже 10 дней подряд без перерасхода 💪».\nВ конце недели — короткий отчёт: «Ты сэкономил 1800₽, что почти равняется походу в кафе».\n3. За 5–7 дней до конца бесплатного периода\nМягкие уведомления:\n«Через неделю твой бесплатный месяц закончится. Хочешь продолжить?»\nКнопки: Оформить подписку → 1 мес / 3 мес / 6 мес.\n4. После окончания\nЛимит блокируется, но данные сохраняются.\nСообщение: «Твой бесплатный месяц закончился. Чтобы продолжить вести бюджет, оформи подписку 👇».\n🎯 Фишки для удержания\nОтчёты: раз в неделю бот высылает короткий PDF/картинку с итогами.\nНапоминания: в одно и то же время (можно настроить) «Внеси траты за день».\nСравнение: «Ты тратишь на еду на 20% меньше, чем средний пользователь бота».\nПодарочные подписки (друг пригласил — +7 дней бесплатного).','\n',char(10)),NULL,'{}','new','medium','bot','medium',35000.0,7000.0,NULL,5,NULL,'2025-08-31 00:00:00.000000','2025-08-22 08:38:20.972524','2025-10-29 10:01:29.608086','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-22T08:38:20.983061", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',1,NULL,17500.0,17500.0,0.0,'default',0,NULL,NULL,'2025-08-22 08:38:20.975480',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(21,23,'Бот КП метал',replace('Бот должен : \n1.⁠ ⁠Принимать заявку на закупку от менеджера (фото или текст или файл)\n2.⁠ ⁠⁠конвертировать в единый текстовый формат с тоннажность , штуками , метрами и поставщиком(всё кратно позициям) если это труба 12 или 6м  , если это арматура 11.7м или 6м  всё в зависимости от позиции длинны позиций можно посмотреть в прайсе\n3.⁠ ⁠искать лучший вариант на площадке ( эксель таблица) с выбором позиций если у поставщика у которого лучшие цены может взять от туда 2-3 позиции по лучшей цене , а остальные по средней цене что бы закрывать заявку с 1 места , в случае если всё в 1 месте нет то по лучшим ценам \n4.⁠ ⁠⁠выдавать результат в текстовом виде в ТГ бот , если позиции которых не нашел в списке выдает эти товары с стоимость -0 без поставщика ( дальше менеджер сам подставит туда цены и отправит в чат ) \n5.⁠ ⁠Возможность создавать наценку на товар (пример мы хотим размазать 20000р маржинальности на товары он их раскидывает по всем позициям в равных долях )\n5.⁠ ⁠⁠формировать ПДФ и EXEL файл для редакции в виде коммерческого предложения с НДС 20% (в коммерческом не нужно указывать поставщика)','\n',char(10)),NULL,'{}','accepted','medium','bot','medium',35000.0,7000.0,NULL,0,NULL,'2025-08-28 00:00:00.000000','2025-08-22 08:42:52.981927','2025-10-29 10:01:07.425940','{"created_manually": true, "created_by": "admin", "created_at": "2025-08-22T08:42:52.998703", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',1,NULL,17500.0,17500.0,0.0,'default',0,NULL,NULL,'2025-08-22 08:42:52.986547',NULL,NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(22,36,'4 Бота для Wildberries ( внедрить)','надо сделать 4 проекта для вайлдбериз логистики ( они уже готовы)',NULL,'{}','завершен','low','bot','medium',200000.0,10000.0,NULL,10,NULL,NULL,'2025-09-03 10:02:38.160492','2025-09-29 08:04:14.240546','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-03T10:02:38.180300", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,100000.0,300000.0,0.0,'default',1,NULL,NULL,'2025-09-03 10:02:38.164085','2025-09-05 16:02:38.160425',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(23,37,'Бот для учета фоток Транспортных  средств',replace('Круто, ты уже чётко описал чек-лист. Давай сразу сведу это в рабочую схему бота + куда девать фото + распределение ответственности и сроки.\n\nКак будет работать бот (Telegram)\n\nРоли: Водитель, Ответственный за авто (механик/куратор), Админ региона.\n\nРегион и доступ: каждому пользователю задаётся region_id. Списки авто/отчётов показываются только по его региону.\n\nФлоу водителя\n 1. Регистрация: ФИО, номер маршрута, выбор авто из списка своего региона (или по госномеру/ID).\n 2. Осмотр “Перед сменой”: бот ведёт по шагам и не даст “Закрыть”, пока не загружены нужные кадры:\n • Бок слева\n • Бок справа\n • Зад\n • Повреждения (если есть)\n • Под капотом\n • Уровни жидкостей\nДополнительно: пробег (одометр), уровень топлива, геолокация (по желанию), время — автоматически.\n 3. Недочёты (текст + фото): чекбокс-категории (тормоза, свет, шины, кузов, жидкости, салон, прочее) + свободный текст и фото.\n 4. Закрытие смены: водитель отмечает новые/обнаруженные в процессе недочёты.\n 5. Квитанция: бот показывает краткий акт приёмки/сдачи (до/после) — можно скачать PDF.\n\nФлоу ответственного\n • Получает уведомление о каждом новом недочёте по “своим” авто.\n • В карточке недочёта ставит: стадию (новый → в работе → решён), срок (дата), исполнитель (если есть), комментарии, стоимость/часы.\n • Может закрыть несколько недочётов одним действием (“после ТО-2 закрыть №…”) + добавить фото-подтверждение.\n\nФлоу админа региона\n • Управление списком авто/водителей/ответственных.\n • Просмотр реестра по авто, выгрузка XLSX/PDF, фильтры по срокам/стадиям.\n • Настройка чек-листов (что обязательно фоткать) — можно сделать разный набор для разных регионов.\n\n⸻\n\nКуда отправлять фото — варианты\n 1. S3-совместимое хранилище (рекомендую):\n • Варианты: Yandex Object Storage / VK Cloud / Selectel / любой S3 (или on-prem MinIO).\n • Плюсы: дёшево, быстро, надёжно, пресайнд-URL для безопасной выдачи, lifecycle-политики (хранить оригинал 1 год, превью — дольше).\n • Минусы: нужна простая обвязка (бэкенд) для загрузки/доступа.\n 2. Google Drive по папкам (быстрый старт): регион → авто → дата/смена.\n • Плюсы: супер просто, сразу превью/шаринг.\n • Минусы: медленнее, сложнее с правами/автоматикой, лимиты.\n 3. Хранить только file_id Telegram (не рекомендую как единственное):\n • Плюс: быстро. Минус: зависимость от Telegram, нет гарантий долгого хранения/доступа вне ТГ.\n\nРабочая схема: загрузили фото в Telegram → бэкенд скачал и положил в S3 → сохранил s3_url + telegram_file_id в БД → в админке/отчётах даём краткоживущие presigned URLs.\n\n⸻\n\nАвто-распределение недочётов и SLA\n • У каждой машины есть ответственный (user_id). По умолчанию все новые недочёты по этой машине назначаются на него.\n • Можно настроить правила: по категории дефекта (электрика → Иванов, ходовая → Петров).\n • Бот просит срок при назначении; если не задан — подставляет “по умолчанию” (напр., 3 рабочих дня).\n • Напоминания: за 24ч до дедлайна, в день дедлайна, и эскалация админу региона при просрочке.\n • Дашборд: “красные” просрочки, ТО на подходе, топ-проблемы по авто/водителям.\n\n⸻\n\nСтруктура данных (минимальная)\n\nRegion(id, name)\nUser(id, tg_id, fio, role, region_id, route_number, is_active)\nVehicle(id, region_id, plate, name, vin?, responsible_user_id)\nShift(id, vehicle_id, driver_user_id, start_ts, end_ts, start_odometer, end_odometer, start_fuel, end_fuel)\nInspection(id, shift_id, type: ''pre''|''post'', ts, geo_lat?, geo_lon?, notes)\nInspectionPhoto(id, inspection_id, kind: ''left''|''right''|''rear''|''damage''|''under_hood''|''fluids'', s3_url, tg_file_id)\nIssue(id, vehicle_id, created_by_user_id, created_ts, category, description, status: ''new''|''in_work''|''resolved'', due_date?, assignee_user_id)\nIssuePhoto(id, issue_id, s3_url, tg_file_id)\nIssueComment(id, issue_id, user_id, ts, text, s3_url?)\n\n\n⸻\n\nИнтерфейс в Telegram (пример)\n • Главное меню водителя: Начать смену · Завершить смену · Мои авто · Инструкции\n • “Начать смену” → выбор авто → пошаговый фоточеклист (бот не даст пропустить обязательные).\n • “Завершить смену” → добавить недочёты/фото → итоговая карточка.\n• Ответственным: Мои задачи → список с кнопками: В работу, Срок, Назначить, Закрыть, Комментарий, Фото.\n • Админу: Авто, Водители, Недочёты, Отчёты.\n\n⸻\n\nОтчёты/реестры\n • Реестр недочётов по авто (то, что ты просишь): фильтры по статусу/сроку/категории/водителю.\n • Экспорт XLSX/PDF + еженедельная рассылка в ТГ/почту по региону.\n • “Акт приёмки-сдачи” по смене: до/после, набор фото, подписи (имя в ТГ + штамп времени/локации).\n\n⸻\n\nАнти-фрод и качество данных\n • Требовать геолокацию и одометр (фото приборки) при предосмотре.\n • Проверять, что пост-осмотр не старше N минут после “Завершить смену”.\n • Лимит по времени между “пред” и “пост” (например, ≤ 16 ч).\n • Фото-валидаторы: минимальное разрешение, не ч/б, свежесть (по EXIF, если доступна).\n\n⸻\n\nТехнологии (MVP)\n • Bot: Telegram + aiogram (Python) или grammY (Node.js).\n • Бэкенд/API: Python FastAPI / Node NestJS.\n • БД: PostgreSQL.\n • Хранилище фото: S3 (Yandex/Selectel/VK Cloud или MinIO).\n • Админка: простая веб-панель (Next.js) или прямо в ТГ-интерфейсе + еженедельные выгрузки.\n • Хостинг: любой VPS/облако; логи — Grafana/Loki, алерты — в ТГ.\n\n⸻\n\nЧто дам на старте\n 1. Чек-лист по умолчанию (можно править по регионам):\n\nrequired_photos_pre = [left, right, rear, under_hood, fluids]\nrequired_photos_post = [damage?]  # обязательны только если есть жалобы\nissue_categories = [тормоза, свет, шины, жидкости, кузов, салон, прочее]\n\n 2. Роли и права.\n 3. Схему БД/миграции.\n 4. S3-папки: region/vehicle/YYYY-MM-DD/shift-<id>/pre/*.jpg и .../post/*.jpg.\n 5. Экспорт реестра (XLSX) + шаблон еженедельного отчёта.\n\n⸻\n\nОтветы на твои вопросы коротко\n • Куда фото: лучше S3 (Yandex/VK/Selectel или MinIO). Хранить оригинал + превью, доступ по presigned URL, срок жизни ссылок — 24 ч.\n • Как распределять недочёты: по ответственному за авто (по умолч.) + правила по категориям.\n • Как ставить даты решения: ответственный выбирает срок в карточке; бот сам напоминает и эскалирует.\n\nХочешь — соберу тебе минимальный ТЗ с экранными сценариями и SQL-схемой “как есть”, чтобы можно было сразу отдавать в разработку.','\n',char(10)),NULL,'{}','overdue','medium','website','medium',70000.0,13999.999999999999999,NULL,0,NULL,NULL,'2025-09-03 10:23:36.038145','2025-10-29 10:00:41.585868','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-03T10:23:36.067090", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',3,NULL,0.0,70000.0,0.0,'default',0,NULL,NULL,'2025-09-03 10:23:36.041009','2025-09-10 10:23:36.038109',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(24,38,'Бот продажник по категориям Техника',replace('Кнопки \n\niPhone \nMacBook \nAirPods\nApple Watch \niPad \nАксессуары Apple \nSamsung \nSony \nMarshall\nЯндекс \nDyson \nБ/У Техника','\n',char(10)),NULL,'{}','завершен','medium','bot','medium',10000.0,2000.0,NULL,0,NULL,NULL,'2025-09-11 05:23:17.356211','2025-09-29 08:04:26.775531','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-11T05:23:17.380618", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,5000.0,5000.0,0.0,'default',1,NULL,NULL,'2025-09-11 05:23:17.359255','2025-09-18 05:23:17.356162',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(25,39,'Бот для перевозчика ВБ','ы хотите бота, в который можно загрузить список штрих-кодов и количество товара, указать количество машин/ТС, а бот автоматически распределит товар по машинам так, чтобы получилось равномерно и без ручных расчётов. При этом он должен учитывать расстояния — чтобы каждая машина проехала как можно меньше километров, а маршруты были оптимальными.',NULL,'{}','завершен','medium','bot','medium',30000.0,6000.0,NULL,0,NULL,NULL,'2025-09-11 05:27:42.934904','2025-09-29 08:04:47.249019','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-11T05:27:42.953136", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,'2025-09-11 05:27:42.936786','2025-09-18 05:27:42.934824',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(26,40,'БОТ остатки ПМ','БОТ остатки ПМ',NULL,'{}','завершен','medium','website','medium',35000.0,2500.0,NULL,0,NULL,NULL,'2025-09-19 15:10:26.243294','2025-09-29 08:05:16.424510','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-19T15:10:26.261726", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,0.0,15000.0,0.0,'default',1,NULL,NULL,'2025-09-19 15:10:26.244902','2025-09-26 15:10:26.243238',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(27,41,'БОТ остатки ПМ','БОТ остатки ПМ',NULL,'{}','завершен','medium','website','medium',25000.0,2000.0,NULL,0,NULL,NULL,'2025-09-19 15:14:08.953234','2025-09-29 08:05:05.656682','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-19T15:14:08.967125", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,'2025-09-19 15:14:08.955833','2025-09-26 15:14:08.953092',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(28,42,'БОТ остатки ПМ 1шт','БОТ остатки ПМ',NULL,'{}','завершен','medium','website','medium',35000.0,NULL,NULL,0,NULL,NULL,'2025-09-19 15:22:41.877514','2025-09-29 08:05:26.118282','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-19T15:22:41.887162", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',5,NULL,0.0,0.0,0.0,'default',1,NULL,NULL,'2025-09-19 15:22:41.879078','2025-09-26 15:22:41.877466',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(29,43,'Mini App гид по местам',replace('Стартовый этап (MVP, 2–3 недели):\n– Категории «Где поесть» и «Куда пойти»\n– Добавление объявлений с фото, описанием, контактами\n– Карточка заведения/мероприятия с кнопкой «Посмотреть контакты и карту»\n– Простая сортировка по категориям\n– Мини-админка для модерации\n\nТак вы уже получите рабочий сервис, который можно тестировать с реальными заведениями и пользователями.\n\nСледующие этапы (опционально, по приоритету):\n– Фильтры по городу, времени, ценам\n– Меню/доставка внутри карточки\n– Подключение оплаты (например, Swish или аналоги) с учётом того, что средства идут напрямую заведению, а сервис получает % комиссии\n– Донации/чаевые (округление суммы, выбор фонда)\n– Реферальная система приглашений\n\nПо платежам: если Swish подходит, можем интегрировать его. В Telegram также есть Telegram Payments, можно подключить его или внешние платёжки (например, Stripe/ЮKassa, если будет запуск в РФ). Мы можем обсудить оптимальный вариант, чтобы было и удобно, и безопасно.','\n',char(10)),NULL,'{}','overdue','medium','app','medium',150000.0,35000.0,NULL,0,NULL,NULL,'2025-09-30 09:55:43.118097','2025-10-07 15:25:50.496097','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-30T09:55:43.128004", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',1,NULL,35000.0,35000.0,0.0,'default',0,NULL,NULL,'2025-09-30 09:55:43.119556','2025-10-07 09:55:43.118056',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(30,44,'Бот удаление штампов',replace('4. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ\n\n4.1. Базовый функционал Telegram-бота\n\n4.1.1. Регистрация и авторизация\n\n• При первом обращении к боту пользователь проходит простую регистрацию (имя, контактные данные — опционально)\n• Для внутреннего использования ООО "ЭЛЕМЕНТ" предусмотрен доступ по белому списку пользователей (Telegram ID)\n4.1.2. Загрузка файлов\n\n• Пользователь отправляет PDF-файл чертежа в бот\n• Бот принимает файлы размером до 20 МБ (ограничение Telegram API)\n• Для больших файлов предусмотрена возможность отправки через внешние облачные хранилища (Google Drive, Яндекс.Диск) с последующей загрузкой по ссылке\n4.1.3. Обработка файлов\n\n• Бот информирует пользователя о начале обработки\n• Отображается статус обработки (конвертация, анализ, удаление штампов, формирование PDF)\n• При возникновении ошибок бот уведомляет пользователя и предлагает повторить попытку\n4.1.4. Получение результата\n\n• После завершения обработки бот отправляет пользователю очищенный PDF-файл\n• Предусмотрена возможность предварительного просмотра результата (первая страница в формате изображения)\n• Пользователь может подтвердить результат или запросить повторную обработку с другими параметрами\n4.1.5. История обработки\n\n• Пользователь может запросить список ранее обработанных файлов\n• Возможность повторной загрузки результатов в течение определенного периода (например, 7 дней)\n4.2. Модуль распознавания и удаления штампов\n\n4.2.1. LLM-модель распознавания\n\n• Модель обучена на датасете чертежей с различными типами штампов, подписей и графических элементов\n• Модель определяет координаты (bounding boxes) штампов на растровом изображении\n• Поддержка различных форматов штампов: прямоугольные, круглые, произвольной формы\n• Модель способна распознавать текстовые и графические элементы штампов\n4.2.2. Алгоритм удаления\n\n• После идентификации координат штампа алгоритм удаляет графические элементы в этой области\n• Используются методы inpainting (восстановления изображения) для заполнения области удаленного штампа фоном или паттерном, соответствующим окружающей области чертежа\n• Сохранение исходного качества изображения и резкости линий чертежа\n4.2.3. Контроль качества\n\n• Автоматическая проверка результата обработки (отсутствие артефактов, сохранение читаемости чертежа)\n• В случае низкого качества результата пользователю предлагается ручная корректировка или повторная обработка\n4.3. Система монетизации и подписок\n\n4.3.1. Бизнес-модель\n\n• Для сотрудников ООО "ЭЛЕМЕНТ": бесплатный доступ (белый список)\n• Для внешних пользователей: модель подписки или оплаты за обработку\n4.3.2. Тарифные планы (для внешних пользователей)\n\n• Бесплатный пробный период: 3 файла бесплатно для ознакомления\n• Базовый тариф: 500 рублей/месяц — до 50 файлов\n• Стандартный тариф: 1500 рублей/месяц — до 200 файлов\n• Профессиональный тариф: 3000 рублей/месяц — до 500 файлов\n• Корпоративный тариф: индивидуальные условия для компаний\n4.3.3. Платежная система\n\n• Интеграция с ЮKassa или CloudPayments\n• Поддержка оплаты банковскими картами\n• Автоматическое продление подписки\n• Уведомления о статусе подписки и приближающемся окончании периода\n4.3.4. Административная панель\n\n• Веб-интерфейс для управления пользователями, подписками и статистикой\n• Мониторинг финансовых транзакций\n• Управление тарифными планами и ценообразованием\n• Просмотр истории обработки файлов и аналитики использования','\n',char(10)),NULL,'{}','overdue','medium','bot','medium',75000.0,15000.0,NULL,20,NULL,NULL,'2025-09-30 10:01:23.248204','2025-10-29 10:00:00.738693','{"created_manually": true, "created_by": "admin", "created_at": "2025-09-30T10:01:23.257956", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',5,NULL,0.0,35000.0,0.0,'default',0,NULL,NULL,'2025-09-30 10:01:23.249667','2025-10-03 22:01:23.248160',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(31,45,'Telegram Mini App - игры PS','ТЗ есть в сообщениях с клиентом',NULL,'{}','overdue','medium','app','medium',500000.0,150000.0,NULL,100,NULL,NULL,'2025-10-10 18:48:22.315943','2025-10-29 09:58:53.664466','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-10T18:48:22.335733", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',4,NULL,250000.0,329999.99999999999999,0.0,'default',0,NULL,NULL,'2025-10-10 18:48:22.320275','2025-10-24 06:48:22.315874',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(32,46,'TMA - кондиционеры','ТЗ есть в личном чате с клиентом',NULL,'{}','overdue','medium','website','medium',100000.0,NULL,NULL,0,NULL,NULL,'2025-10-10 18:50:10.302614','2025-10-18 00:32:46.295534','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-10T18:50:10.321465", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',4,NULL,60000.0,60000.0,0.0,'default',0,NULL,NULL,'2025-10-10 18:50:10.304843','2025-10-17 18:50:10.302557',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(33,47,'TMA - агрегатор нейросетей',replace('1. Минимальная версия (MVP)\n\nЦель: быстро запустить рабочий прототип и протестировать идею.\n\nЧто входит:\n\nTelegram Mini App с авторизацией и базовым UI\n\nПодключение одной нейросети (например, GPT-4 или Mistral)\n\nПростая история запросов\n\nмногопоточность отсутствует ( до 50 пользователей одновременно)\n\nРучное управление балансом/лимитами\n\nМинимальный админ-функционал через команды\n\n\n\n\n2. Расширенная версия\n\nЦель: сделать удобный продукт с оплатой и несколькими AI-провайдерами.\n\nЧто входит:\n\nВсё из MVP\n\nПодключение 6 моделей\n\nСистема тарифов и баланса ( расширенная + гибкое управление через админку)\n\nРеферальная система гибкая \n\nподдержка 3 месяца после разработки бесплатно далее 10-25 тысяч\n\nрасширенная админ-панель в Mini App\n\nкрасивый проработанный дизайн \n\nмногопоточность до 300 пользователей одновременно\n\n3. Полная версия (коммерческий релиз)\n\nЦель: готовый стабильный агрегатор с инфраструктурой и аналитикой.\n\nЧто входит:\n\nВсё из расширенной версии\n\nАрхитектура с двумя серверами (локальный + зарубежный)\n\nАвтоматические подписки и продления\n\nМетрики, мониторинг, алерты\n\nПоддержка генерации картинок/аудио+ интеграция VEO 3 ( бесшовная) + higgsfield\n\nВеб-интерфейс администратора ( отдельная страница на reacts + vue) как сайт \n\nСрок: 9–12 недель\nСтоимость: от 250000 ₽','\n',char(10)),NULL,'{}','overdue','medium','app','medium',200000.0,75000.0,NULL,0,NULL,NULL,'2025-10-10 18:53:36.793770','2025-10-30 16:57:51.198759','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-10T18:53:36.806128", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',9,NULL,0.0,40000.0,0.0,'default',0,NULL,NULL,'2025-10-10 18:53:36.795546','2025-10-17 18:53:36.793719',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(34,48,'TMA - гид по городам (ШИЛОВ)','в личных сообщениях с клиентом',NULL,'{}','accepted','high','website','complex',350000.0,150000.0,NULL,0,NULL,NULL,'2025-10-10 18:56:45.508009','2025-10-10 18:56:45.521881','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-10T18:56:45.520677", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',7,NULL,188999.99999999999999,188999.99999999999999,0.0,'default',0,NULL,NULL,'2025-10-10 18:56:45.510205','2025-10-17 18:56:45.507932',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(35,49,'Бот для рассчета ЗП перевозчик',replace('аходим в вб ол и выгружаем путевые за опредлененный период , далее открываем отчет и нужно релизовать систему для 2 вариантов когда подрядчики работаю на проценте и на ставке далее делаем базовую админку с возможность внесения контараагентов и выбором условий рассчетов ( процент или ставка для них) также должна быть информация по номеру автомобиля который привязан к перевозчику ( они все ИПшники) если будет собственный транспорт выбираем себя как контрагента.\n\nЕсли мы берем магистраль "собственный транспорт __. то рассчет зп происходит по следюущей формуле это кол-во километров на X ( в средне 10-12 рублей) и суточные ( опционально кто то платит кто нет ) \n\nдалее делаем базовую аналитику ( два варианта - аналитка по наемному транспорту и по собственному )\n\nкак метрики должны быть - 1 столбец запрлпата водителя , километраж сколько он проехал , топливный расход ( спарсить инфу с ЛК водителя и посмотреть сколько топлива он потратил) , расходы по автомобилю ( как правило эту инфу предоставляет штатный механик если механика нет то это руководитель делает или ответтсвенное лицо)\n\nесли автомобиль больше 12 тонн то нужно учитывать дополнительно расходы по оплате ПЛАТОН (возмещение ущерба дорог)\n\nрасходы по транспондерам ( также учитывать) эту информацию предоставляет либо руководитель ( есть лк ) \n\nТО также нужно сделать рассчет данной стоимости - отдел механиков вносит , если механик не вносит то руководитель вносит','\n',char(10)),NULL,'{}','overdue','medium','bot','medium',35000.0,7000.0,NULL,0,NULL,NULL,'2025-10-10 19:01:06.401000','2025-10-18 17:08:03.996718','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-10T19:01:06.425989", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',4,'2025-10-18 17:08:03.996714',18500.0,18500.0,0.0,'default',0,NULL,NULL,'2025-10-10 19:01:06.403227','2025-10-17 19:01:06.400945',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(36,1,'Mini App для детей ','Красиво четко ',NULL,'{"quick_request": true, "budget": "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d", "deadline": "\u041a\u0430\u043a \u043c\u043e\u0436\u043d\u043e \u0431\u044b\u0441\u0442\u0440\u0435\u0435"}','overdue','normal','telegram_miniapp','medium',0.0,NULL,NULL,0,NULL,NULL,'2025-10-18 08:07:45.543633','2025-10-25 09:00:38.728889','{"bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"}',4,'2025-10-18 17:08:03.996761',0.0,0.0,0.0,'default',1,NULL,NULL,'2025-10-18 08:07:45.543625','2025-10-25 08:07:45.527687',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(37,51,'Телеграм БОТ для пенсионеров ( отметки в приложении)',replace('Как мы делаем сейчас :\n\n1.⁠ ⁠У нас идет урок онлайн по 1 часу. \n2.⁠ ⁠⁠на 40 минуте мы делаем скрины занятий (там должно дать время и дата, и название конференции )\n3.⁠ ⁠⁠после того как урок прошел, мы в течение часа должны отметить участников по скринам','\n',char(10)),NULL,'{}','overdue','medium','bot','medium',120000.0,24000.0,NULL,0,NULL,NULL,'2025-10-20 14:41:23.641135','2025-10-27 16:10:26.807393','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-20T14:41:23.671521", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',5,NULL,40000.0,40000.0,0.0,'default',0,NULL,NULL,'2025-10-20 14:41:23.656830','2025-10-27 14:41:23.641090',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(38,53,'Бот доступ к курсу ( регистрация товарных знаков)','Бот доступ к курсу',NULL,'{}','overdue','medium','bot','medium',45000.0,9000.0,NULL,0,NULL,NULL,'2025-10-20 14:47:23.433461','2025-10-27 16:10:26.807393','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-20T14:47:23.445292", "edit_history": [], "bot_token": "-", "timeweb_login": null, "timeweb_password": null}',3,NULL,22500.0,22500.0,0.0,'default',0,NULL,NULL,'2025-10-20 14:47:23.439679','2025-10-27 14:47:23.433405',NULL,0.0,NULL,NULL,NULL);
INSERT INTO projects VALUES(39,55,'Телеграм бот для автоматизации управления каналами',replace('Light-версия (минималка) — 70 000 руб., срок 4–5 недель. В неё войдёт:\n    •    подключение канала и авторизация бота\n    •    создание и планирование постов с автопубликацией\n    •    генерация 2–3 вариантов текста через AI по короткому ТЗ\n    •    простая кнопка монетизации (донат или заказ услуги)\n    •    базовый лог публикаций и уведомления об ошибках\nВ этой версии не будет продвинутой аналитики, сложных платежных интеграций, веб-панели и автоматизации без подтверждения. Но этого достаточно, чтобы протестировать идею и начать пользоваться ботом, а потом уже постепенно развивать его дальше.','\n',char(10)),NULL,'{}','overdue','low','bot','medium',70000.0,13999.999999999999999,NULL,0,NULL,NULL,'2025-10-24 11:10:32.124796','2025-10-31 14:06:19.896164','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-24T11:10:32.153737", "edit_history": [], "bot_token": null, "timeweb_login": null, "timeweb_password": null}',8,NULL,35000.0,35000.0,0.0,'default',0,NULL,NULL,'2025-10-24 11:10:32.132271','2025-10-31 11:10:32.124758',NULL,0.0,'234263417',NULL,NULL);
INSERT INTO projects VALUES(40,56,'Telegram-бот для продажи доступа к закрытым каналам','Нужен бот для монетизации закрытых каналов',NULL,'{}','overdue','low','bot','medium',40000.0,8000.0,NULL,0,NULL,'2025-10-30 21:00:00.000000','2025-10-24 11:51:06.993637','2025-10-31 08:24:30.091632','{"created_manually": true, "created_by": "admin", "created_at": "2025-10-24T11:51:07.015048", "edit_history": [], "bot_token": null, "tz_file_path": null, "tz_file_original_name": null}',5,NULL,20000.0,20000.0,0.0,'default',0,NULL,NULL,'2025-10-24 11:51:06.996437','2025-10-31 00:00:00.000000',NULL,0.0,'403053379',NULL,NULL);
INSERT INTO projects VALUES(48,66,'БОТ ТЕЛЕГРАМ','кшгарагрцкшгаркг',NULL,'{}','overdue','medium','bot','medium',0.0,10000.0,NULL,0,NULL,NULL,'2025-11-02 10:49:51.896074','2025-11-09 11:29:45.903643','{"created_manually": true, "created_by": "admin", "created_at": "2025-11-02T10:49:51.937532", "edit_history": [], "tz_file_path": null, "tz_file_original_name": null}',11,NULL,0.0,0.0,0.0,'default',0,NULL,NULL,'2025-11-02 10:49:51.907297','2025-11-09 10:49:51.896038',NULL,0.0,'6898088562',NULL,'pythongodbless');
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
INSERT INTO finance_categories VALUES(1,'Проекты - Разработка ботов','income','Доходы от разработки Telegram-ботов','#28a745','fas fa-robot',1,'2025-07-10 17:57:04.297857',1);
INSERT INTO finance_categories VALUES(2,'Проекты - Веб-разработка','income','Доходы от веб-разработки','#17a2b8','fas fa-globe',1,'2025-07-10 17:57:04.297920',1);
INSERT INTO finance_categories VALUES(3,'Консультации','income','Доходы от консультаций','#20c997','fas fa-handshake',1,'2025-07-10 17:57:04.297940',1);
INSERT INTO finance_categories VALUES(4,'Дополнительные услуги','income','Настройка серверов, домены и прочее','#6f42c1','fas fa-tools',1,'2025-07-10 17:57:04.297953',1);
INSERT INTO finance_categories VALUES(5,'Бонусы и премии','income','Бонусные выплаты от клиентов','#fd7e14','fas fa-gift',1,'2025-07-10 17:57:04.297964',1);
INSERT INTO finance_categories VALUES(6,'Выплаты исполнителям','expense','Оплата работы исполнителей','#dc3545','fas fa-user-tie',1,'2025-07-10 17:57:04.297984',1);
INSERT INTO finance_categories VALUES(7,'Нейросети и API','expense','Расходы на OpenAI, Claude и другие AI-сервисы','#e83e8c','fas fa-brain',1,'2025-07-10 17:57:04.297996',1);
INSERT INTO finance_categories VALUES(8,'Хостинг и серверы','expense','Оплата хостинга, VPS, доменов','#6c757d','fas fa-server',1,'2025-07-10 17:57:04.298005',1);
INSERT INTO finance_categories VALUES(9,'Лицензии и подписки','expense','Софт, инструменты разработки','#007bff','fas fa-key',1,'2025-07-10 17:57:04.298015',1);
INSERT INTO finance_categories VALUES(10,'Реклама и маркетинг','expense','Расходы на продвижение','#ffc107','fas fa-bullhorn',1,'2025-07-10 17:57:04.298024',1);
INSERT INTO finance_categories VALUES(11,'Офисные расходы','expense','Интернет, электричество, прочие расходы','#6f42c1','fas fa-building',1,'2025-07-10 17:57:04.298033',1);
INSERT INTO finance_categories VALUES(12,'Налоги и сборы','expense','Налоги, комиссии банков','#dc3545','fas fa-receipt',1,'2025-07-10 17:57:04.298042',1);
INSERT INTO finance_categories VALUES(13,'Обучение и развитие','expense','Курсы, книги, конференции','#17a2b8','fas fa-graduation-cap',1,'2025-07-10 17:57:04.298052',1);
INSERT INTO finance_categories VALUES(14,'Оплата проекта','income','Оплаты от клиентов','#6c757d','fas fa-circle',1,'2025-10-29 09:58:53.650436',NULL);
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
	created_by_id INTEGER NOT NULL, account VARCHAR(50) DEFAULT 'card', 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES finance_categories (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(parent_transaction_id) REFERENCES finance_transactions (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO finance_transactions VALUES(8,750.0,'income','Финальная тестовая транзакция','2025-01-18 14:00:00.000000',1,NULL,NULL,NULL,'Проверяем работу кнопок удаления',0,NULL,NULL,'2025-07-17 22:35:28.167054',0,'card');
INSERT INTO finance_transactions VALUES(9,40000.0,'income','Бот разработка @truetechshop предоплата 40.000 из 80.000','2025-07-18 15:06:00.000000',1,NULL,'Николай',NULL,NULL,0,NULL,NULL,'2025-07-18 15:07:40.896845',0,'card');
INSERT INTO finance_transactions VALUES(10,20000.0,'income','Предоплата за бота по Удержаниям Роман (телеграм pythongodbless) там искать сумма 20000 из 45000','2025-07-20 09:36:00.000000',1,NULL,'Никола',NULL,NULL,0,NULL,NULL,'2025-07-20 09:37:53.016062',0,'card');
INSERT INTO finance_transactions VALUES(11,50000.0,'income','оплата вторая часть за ITCOIN 50000 (остаток 30000)','2025-07-21 14:25:00.000000',1,NULL,'Паша',NULL,NULL,0,NULL,NULL,'2025-07-21 14:26:03.472857',0,'card');
INSERT INTO finance_transactions VALUES(12,40000.0,'income','Бот по продаже цифровых товаров 40000 ( выплаачено 80000 из 80000)','2025-07-23 22:13:00.000000',1,NULL,'Никола',NULL,NULL,0,NULL,NULL,'2025-07-23 22:14:48.702278',1,'card');
INSERT INTO finance_transactions VALUES(13,25000.0,'income','Транзакция из чека receipt_501613334_1754291781.jpg','2025-08-03 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291781.jpg','OCR данные: {"success": true, "amount": 25000.0, "date": "2025-08-03T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 25000,\n    \"date\": \"03.08.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:16:37.171025',2,'card');
INSERT INTO finance_transactions VALUES(14,10000.0,'income','Транзакция из чека receipt_501613334_1754291804.jpg','2025-07-30 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291804.jpg','OCR данные: {"success": true, "amount": 10000.0, "date": "2025-07-30T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": \"10000\",\n    \"date\": \"30.07.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1.0\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:17:02.660866',2,'card');
INSERT INTO finance_transactions VALUES(15,80000.0,'income','Транзакция из чека receipt_501613334_1754291831.jpg','2025-08-01 00:00:00.000000',1,NULL,NULL,'uploads/receipts/receipt_501613334_1754291831.jpg','OCR данные: {"success": true, "amount": 80000.0, "date": "2025-08-01T00:00:00", "organization": "озон банк", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 80000,\n    \"date\": \"01.08.2025\",\n    \"organization\": \"озон банк\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 07:17:19.358795',2,'card');
INSERT INTO finance_transactions VALUES(16,5000.0,'expense','Транзакция из чека receipt_501613334_1754298071.jpg','2025-08-04 00:00:00.000000',10,NULL,NULL,'uploads/receipts/receipt_501613334_1754298071.jpg','OCR данные: {"success": true, "amount": 5000.0, "date": "2025-08-04T00:00:00", "organization": "ООО \"КЕХ ЭКОММЕРЦ\"", "confidence": 1.0, "raw_response": "```json\n{\n    \"amount\": 5000,\n    \"date\": \"04.08.2025\",\n    \"organization\": \"ООО \\\"КЕХ ЭКОММЕРЦ\\\"\",\n    \"success\": true,\n    \"confidence\": 1\n}\n```", "source": "ai_ocr"}',0,NULL,NULL,'2025-08-04 09:01:26.806392',2,'card');
INSERT INTO finance_transactions VALUES(17,50000.0,'expense','lty','2025-08-06 22:16:37.180000',7,NULL,NULL,NULL,'Быстрая транзакция',0,NULL,NULL,'2025-08-06 22:16:39.497121',2,'card');
INSERT INTO finance_transactions VALUES(18,80000.0,'income','stage по проекту #31: Telegram Mini App - игры PS','2025-10-28 00:00:00.000000',14,31,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 09:58:53.666205',1,'card');
INSERT INTO finance_transactions VALUES(19,40000.0,'income','prepayment по проекту #33: TMA - агрегатор нейросетей','2025-10-15 00:00:00.000000',14,33,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 09:59:42.248849',1,'card');
INSERT INTO finance_transactions VALUES(20,35000.0,'income','prepayment по проекту #30: Бот удаление штампов','2025-10-29 00:00:00.000000',14,30,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 10:00:00.743490',1,'card');
INSERT INTO finance_transactions VALUES(21,70000.0,'income','final по проекту #23: Бот для учета фоток Транспортных  средств','2025-10-16 00:00:00.000000',14,23,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 10:00:41.586375',1,'card');
INSERT INTO finance_transactions VALUES(22,17500.0,'income','prepayment по проекту #21: Бот КП метал','2025-09-18 00:00:00.000000',14,21,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 10:01:07.426408',1,'card');
INSERT INTO finance_transactions VALUES(23,17500.0,'income','prepayment по проекту #20: Бот Амели (учет финансы)','2025-10-01 00:00:00.000000',14,20,NULL,NULL,NULL,0,NULL,NULL,'2025-10-29 10:01:29.608641',1,'card');
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
INSERT INTO contractors VALUES(1,'Алексей Иванов','Опытный Python-разработчик, специализируется на создании Telegram-ботов','{"email": "alexey.ivanov@email.com", "phone": "+7 (999) 123-45-67", "telegram": "@alexey_dev"}','["Python", "Telegram Bot API", "PostgreSQL", "FastAPI", "Docker"]',2000.0,25000.0,4.7999999999999998223,'active','2025-07-09 09:11:54.699613','2025-07-09 09:11:54.699617');
INSERT INTO contractors VALUES(2,'Мария Петрова','Frontend-разработчик с опытом создания веб-интерфейсов','{"email": "maria.petrova@email.com", "phone": "+7 (999) 234-56-78", "telegram": "@maria_frontend"}','["HTML", "CSS", "JavaScript", "React", "Vue.js", "Bootstrap"]',1500.0,20000.0,4.5999999999999996447,'active','2025-07-09 09:11:54.699618','2025-07-09 09:11:54.699618');
INSERT INTO contractors VALUES(3,'Дмитрий Козлов','Fullstack-разработчик, работает с различными технологиями','{"email": "dmitry.kozlov@email.com", "phone": "+7 (999) 345-67-89", "telegram": "@dmitry_fullstack"}','["Python", "JavaScript", "Node.js", "React", "PostgreSQL", "MongoDB"]',2500.0,35000.0,4.9000000000000003552,'active','2025-07-09 09:11:54.699619','2025-07-09 09:11:54.699619');
INSERT INTO contractors VALUES(4,'Елена Смирнова','UI/UX дизайнер с большим опытом в создании пользовательских интерфейсов','{"email": "elena.smirnova@email.com", "phone": "+7 (999) 456-78-90", "telegram": "@elena_design"}','["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator"]',1799.9999999999999999,15000.0,4.7000000000000001776,'active','2025-07-09 09:11:54.699620','2025-07-09 09:11:54.699620');
INSERT INTO contractors VALUES(5,'Андрей Волков','DevOps-инженер, настройка серверов и CI/CD','{"email": "andrey.volkov@email.com", "phone": "+7 (999) 567-89-01", "telegram": "@andrey_devops"}','["Docker", "Kubernetes", "AWS", "Linux", "Nginx", "Jenkins"]',3000.0,40000.0,4.7999999999999998223,'active','2025-07-09 09:11:54.699621','2025-07-09 09:11:54.699621');
INSERT INTO contractors VALUES(6,'Ольга Лебедева','QA-инженер, тестирование веб-приложений и мобильных приложений','{"email": "olga.lebedeva@email.com", "phone": "+7 (999) 678-90-12", "telegram": "@olga_qa"}','["Manual Testing", "Automated Testing", "Selenium", "Postman", "Jest"]',1200.0,12000.0,4.5,'active','2025-07-09 09:11:54.699622','2025-07-09 09:11:54.699622');
INSERT INTO contractors VALUES(7,'Игорь Новиков','Мобильный разработчик, создание iOS и Android приложений','{"email": "igor.novikov@email.com", "phone": "+7 (999) 789-01-23", "telegram": "@igor_mobile"}','["Swift", "Kotlin", "Flutter", "React Native", "iOS", "Android"]',2200.0,30000.0,4.5999999999999996447,'active','2025-07-09 09:11:54.699622','2025-07-09 09:11:54.699623');
INSERT INTO contractors VALUES(8,'Татьяна Морозова','Контент-менеджер и копирайтер','{"email": "tatyana.morozova@email.com", "phone": "+7 (999) 890-12-34", "telegram": "@tatyana_content"}','["Copywriting", "Content Management", "SEO", "Social Media"]',800.0,8000.0,4.4000000000000003552,'active','2025-07-09 09:11:54.699623','2025-07-09 09:11:54.699623');
INSERT INTO contractors VALUES(9,'Владимир Сидоров','Консультант по IT-проектам (временно неактивен)','{"email": "vladimir.sidorov@email.com", "phone": "+7 (999) 901-23-45", "telegram": "@vladimir_consultant"}','["Project Management", "Business Analysis", "Agile", "Scrum"]',2799.9999999999999999,50000.0,4.2999999999999998223,'inactive','2025-07-09 09:11:54.699624','2025-07-09 09:11:54.699624');
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
	actual_time INTEGER, progress INTEGER DEFAULT 0, time_spent_seconds INTEGER DEFAULT 0, timer_started_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(created_by_id) REFERENCES users (id), 
	FOREIGN KEY(assigned_to_id) REFERENCES admin_users (id)
);
INSERT INTO project_revisions VALUES(1,1,1,'Исправить цвет кнопки','Изменить цвет кнопки на главной странице с синего на зеленый','new','medium',7,NULL,'2025-10-18T12:00:20.082910','2025-10-18T12:00:20.082953',NULL,NULL,NULL,0,0,NULL);
INSERT INTO project_revisions VALUES(2,36,1,'Добавить кнопку поделиться','Добавить кнопку для шеринга в социальных сетях','in_progress','high',1,NULL,'2025-10-18 12:05:52','2025-10-18 12:12:55.870642',NULL,NULL,NULL,70,0,NULL);
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
INSERT INTO revision_messages VALUES(1,2,'client',1,NULL,'привет',0,'2025-10-18 12:23:28.131780');
INSERT INTO revision_messages VALUES(2,2,'client',1,NULL,'Акглаиука',0,'2025-10-23 08:13:30.901776');
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
                    task_metadata JSON DEFAULT '{}', color VARCHAR(20) DEFAULT 'normal', progress INTEGER DEFAULT 0, time_spent_seconds INTEGER DEFAULT 0, timer_started_at DATETIME NULL,
                    FOREIGN KEY (assigned_to_id) REFERENCES admin_users (id),
                    FOREIGN KEY (created_by_id) REFERENCES admin_users (id)
                );
INSERT INTO tasks VALUES(50,'Приложение Мини Апп Лига Климата','Доделать приложение миниапп лига климата ( не горит) подправить дизайн возможно что то где то поменять согласуем на созвоне ( не горит)','pending','low',4,1,'2025-09-06 09:37:00.000000',20,NULL,'2025-07-23 06:37:25.628844','2025-09-14 05:30:59.741406',NULL,'{}','red',0,0,NULL);
INSERT INTO tasks VALUES(61,'Таблица умножения Мини Апп',replace(replace('перенести приложение на сервер \r\n\r\n+79152221425. Tatu150489! - юкасса\r\n\r\n\r\nfp93468  Tatu150489! таймбев\r\n\r\n\r\nbagetstroy@gmail.com.  z_nFNyP8 рег ру','\r',char(13)),'\n',char(10)),'pending','low',4,1,'2025-08-06 12:45:00.000000',3,NULL,'2025-08-04 09:45:30.978687','2025-09-14 05:31:18.917275',NULL,'{}','red',0,0,NULL);
INSERT INTO tasks VALUES(96,'Бот парсер цен на трубы ',replace(replace('Бот должен : \r\n1.⁠ ⁠Принимать заявку на закупку от менеджера (фото или текст или файл)\r\n2.⁠ ⁠⁠конвертировать в единый текстовый формат с тоннажность , штуками , метрами и поставщиком(всё кратно позициям) если это труба 12 или 6м  , если это арматура 11.7м или 6м  всё в зависимости от позиции длинны позиций можно посмотреть в прайсе\r\n3.⁠ ⁠искать лучший вариант на площадке ( эксель таблица) с выбором позиций если у поставщика у которого лучшие цены может взять от туда 2-3 позиции по лучшей цене , а остальные по средней цене что бы закрывать заявку с 1 места , в случае если всё в 1 месте нет то по лучшим ценам \r\n4.⁠ ⁠⁠выдавать результат в текстовом виде в ТГ бот , если позиции которых не нашел в списке выдает эти товары с стоимость -0 без поставщика ( дальше менеджер сам подставит туда цены и отправит в чат ) \r\n5.⁠ ⁠Возможность создавать наценку на товар (пример мы хотим размазать 20000р маржинальности на товары он их раскидывает по всем позициям в равных долях )\r\n5.⁠ ⁠⁠формировать ПДФ и EXEL файл для редакции в виде коммерческого предложения с НДС 20% (в коммерческом не нужно указывать поставщика)','\r',char(13)),'\n',char(10)),'pending','high',8,1,'2025-08-31 10:44:00.000000',5,NULL,'2025-08-22 07:44:47.235874','2025-08-22 08:00:28.295346',NULL,'{}','green',0,0,NULL);
INSERT INTO tasks VALUES(97,'Бот Амели ( учет финансов)',replace(replace('Как устроить логику в боте\r\n1. Новый пользователь\r\nПриветствие (дружеское, лёгкое, как мы вчера обсуждали).\r\n«Тебе доступен бесплатный месяц. Веди расходы в 3 категориях и смотри, сколько можно тратить каждый день».\r\nКнопка «Начать».\r\n2. В течение бесплатного месяца\r\nУведомления: «Сегодня твой лимит — 1200₽. Потратил 750₽ — отлично! Остаток можно перенести на завтра».\r\nЛёгкая геймификация: «У тебя уже 10 дней подряд без перерасхода 💪».\r\nВ конце недели — короткий отчёт: «Ты сэкономил 1800₽, что почти равняется походу в кафе».\r\n3. За 5–7 дней до конца бесплатного периода\r\nМягкие уведомления:\r\n«Через неделю твой бесплатный месяц закончится. Хочешь продолжить?»\r\nКнопки: Оформить подписку → 1 мес / 3 мес / 6 мес.\r\n4. После окончания\r\nЛимит блокируется, но данные сохраняются.\r\nСообщение: «Твой бесплатный месяц закончился. Чтобы продолжить вести бюджет, оформи подписку 👇».\r\n🎯 Фишки для удержания\r\nОтчёты: раз в неделю бот высылает короткий PDF/картинку с итогами.\r\nНапоминания: в одно и то же время (можно настроить) «Внеси траты за день».\r\nСравнение: «Ты тратишь на еду на 20% меньше, чем средний пользователь бота».\r\nПодарочные подписки (друг пригласил — +7 дней бесплатного).','\r',char(13)),'\n',char(10)),'in_progress','low',8,1,'2025-08-24 11:00:00.000000',NULL,NULL,'2025-08-22 08:00:21.599096','2025-10-28 20:12:35.585486','2025-10-28 20:11:59.170606','{}','green',0,0,NULL);
INSERT INTO tasks VALUES(166,'Бот для пенсионеров ( отметки ZOOM)',replace(replace('1.⁠ ⁠У нас идет урок онлайн по 1 часу. \r\n2.⁠ ⁠⁠на 40 минуте мы делаем скрины занятий (там должно дать время и дата, и название конференции )\r\n3.⁠ ⁠⁠после того как урок прошел, мы в течение часа должны отметить участников по скринам\r\n\r\nУ нас зум \r\n\r\nУ нас : 5 аккаунтов \r\nУ каждого занятия своя постоянная ссылка.\r\n\r\nТ.е на 1 аккаунте несколько занятий, но не пересекаются по времени \r\n\r\nУчет приложения у нас ооо и ИП, но зум на акаунте есть и ИП и ооо \r\n\r\n\r\n\r\n\r\n','\r',char(13)),'\n',char(10)),'in_progress','low',5,1,'2025-10-31 12:58:00.000000',30,NULL,'2025-10-21 09:59:02.220390','2025-10-25 13:03:37.712757',NULL,'{}','green',30,0,NULL);
INSERT INTO tasks VALUES(169,'Бот скидки ОЗОН реализовать систему выплат','ждем информацию от клиента ( он должен отправить информацию в Юкассу заявку)','in_progress','normal',5,1,'2025-11-09 13:05:00.000000',10,NULL,'2025-10-21 10:05:31.524813','2025-10-23 12:52:06.677087',NULL,'{}','yellow',0,0,NULL);
INSERT INTO tasks VALUES(170,'@check_bot_bobmbbot бот обменник валюты внести правки ',replace(replace('внести правки в данного бота в соответствии с хотелками клиента \r\nНажимаю на кнопку «Обменять» в опубликованном предложении № 123.\r\nПредложение № 123 пересылается в бот пользователя: без кнопки «Обменять»/ либо она деактивируется и в боте пользователя и на канале в этом предложении №123.\r\n- Проверка ФИО (чтобы указали не только 1 слово/ имя)\r\n- когда нажала на «изменить», бот остановился, ответ не пришел.\r\n- должна быть проверка максимального кол-ва цифр в номере карты (сколько обычно? Макс 16?)\r\n-В предпросмотре, когда данные ввела присутствуют кнопки «Изменить» и «Опубликовать». Должно быть «Изменить» и «Подтвердить»\r\n- При «Подтвердить» свой ответ на обмен ответ бота (сколько отправить, куда, отправить чек)\r\n- Неправильный расчёт при ”КУПЛЮ РУБ 10 000 по курсу 5 за 2 000 SEK”\r\nКУПЛЮ РУБ (руб / курс)\r\nПРОДАМ РУБ (руб / курс)\r\nКУПЛЮ SEK (руб * курс)\r\nПРОДАМ SEK (руб * курс)\r\n\r\n-🔔 ОТВЕТ НА ПРЕДЛОЖЕНИЕ #108\r\n👤 Ответил пользователь:\r\nUsername: @nadjaslepova\r\nUser ID: 2027349304\r\nИмя: Nadja\r\nТелефон: +46767119487\r\nОПЛАТА: выбранный способ оплаты\r\nПри оплате укажите № 108\r\n\r\n☘️ Данные получателя:\r\nКарта: 123400005555000066660000\r\nБанк: втб\r\nИмя: Я\r\n\r\n','\r',char(13)),'\n',char(10)),'in_progress','high',5,1,NULL,10,NULL,'2025-10-21 10:07:56.024977','2025-10-25 13:03:17.166025',NULL,'{}','yellow',100,0,NULL);
INSERT INTO tasks VALUES(171,'Сергей боты 2 аккаунта восстановить доступ ','@srgy_ruzhinskyyy - связаться в тг и взять нужную инфу и сдать - у него слетели токены ','completed','normal',5,1,'2025-10-23 13:09:00.000000',5,NULL,'2025-10-21 10:10:00.676148','2025-11-04 07:11:30.144526','2025-11-04 07:11:29.768370','{}','yellow',0,0,'2025-10-22 10:27:38.235375');
INSERT INTO tasks VALUES(172,'Зарплата ВБ перевозчику ( новый бот)','разработка бота для автоматического рассчета зарплаты перевозчикам ','in_progress','normal',5,1,'2025-10-31 13:11:00.000000',10,NULL,'2025-10-21 10:11:21.395257','2025-10-25 13:03:02.271909',NULL,'{}','yellow',80,434,'2025-10-22 10:27:26.008690');
INSERT INTO tasks VALUES(173,'Бот для удаления штампов с PDF','Нужно сделать бота который будет удалять штампы с PDF файлов чертежей и сделать вот таким образом чтобы точность превысила 90%.','completed','normal',9,1,'2025-10-24 14:40:00.000000',5,NULL,'2025-10-21 11:40:35.584922','2025-10-30 08:42:58.874609','2025-10-30 08:42:58.412107','{}','normal',0,0,'2025-10-30 08:42:46.745680');
INSERT INTO tasks VALUES(174,'TMA - Шилов ','сделать тг мини апп для блогера ( ТЗ уже в личных сообщениях) ','pending','normal',7,1,'2025-12-31 14:46:00.000000',100,NULL,'2025-10-21 11:46:25.823205','2025-10-21 11:46:25.823209',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(175,'Бот для регистраци товарных знаков',replace(replace('Предлагаю начать с минимальной точки входа, чтобы быстро протестировать идею и запустить первых пользователей. Такой базовый вариант включает:\r\n	•	Основной Telegram-бот с запуском по /start\r\n	•	Подписку и выдачу уроков 2 раза в неделю\r\n	•	Напоминания об оплате и логику «оплатил второй месяц — первый открылся»\r\n	•	Базовые кнопки и простую админку для добавления уроков\r\n\r\nЭто даст рабочий MVP, с которым можно стартовать и собирать аудиторию, а дальше постепенно наращивать функционал.\r\n\r\n💸 Стоимость такого старта — 45 000 ₽,\r\n⏱️ Срок реализации — 10–14 дней.\r\n\r\nПосле запуска можно будет развивать бота до полноценной версии с защитой контента, расширенной аналитикой и продвинутой логикой монетизации.','\r',char(13)),'\n',char(10)),'in_progress','high',3,1,'2025-10-30 14:51:00.000000',10,NULL,'2025-10-21 11:51:45.446133','2025-10-25 13:06:13.251944',NULL,'{}','green',100,0,NULL);
INSERT INTO tasks VALUES(176,'Сделать бота для ТипоГрафии ( калькулятор)','Техническое задание в личных сообщениях','in_progress','high',8,1,'2025-10-26 14:55:00.000000',10,NULL,'2025-10-21 11:55:52.786520','2025-10-28 20:11:31.667208','2025-10-28 20:11:26.058266','{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(177,'TMA ИИ девушки - разработка дизайна ','Доработать дизайн и внести правки в вестку и отдаем на согласование ','pending','normal',4,1,'2025-10-26 14:58:00.000000',10,NULL,'2025-10-21 11:58:59.249083','2025-10-21 11:58:59.249086',NULL,'{}','green',0,0,NULL);
INSERT INTO tasks VALUES(178,'TMA игры - разработка дизайна (верстка)','Разработать верстку и отдать на соглсование мне и клиенту , тз по дизайну берем из референска @aokis_bot ','completed','normal',4,1,'2025-10-22 23:01:00.000000',10,NULL,'2025-10-21 12:00:27.238745','2025-10-26 10:51:46.381612','2025-10-26 10:51:45.964088','{}','red',0,0,NULL);
INSERT INTO tasks VALUES(179,'TMA Гид по городам внести правки ','обсудили правки с клиентом их нужно сначала согласовать по цене потом внести в приложение и сдать проект на финальную проверку ','in_progress','normal',4,1,'2025-10-31 15:01:00.000000',10,NULL,'2025-10-21 12:01:59.913557','2025-10-26 10:51:36.377290',NULL,'{}','red',25,74080,NULL);
INSERT INTO tasks VALUES(180,'Шмотки - согласовать правки и внести ','Список правок отправлял в ЛС нужно время и цена и брать в работу и закрывать данное приложение ( отправлять на финальный тест)','in_progress','normal',4,1,'2025-10-25 15:03:00.000000',10,NULL,'2025-10-21 12:03:11.085933','2025-11-02 09:56:36.808290',NULL,'{}','red',80,873251,NULL);
INSERT INTO tasks VALUES(185,'Бот доступ к 3 группам приступить ','ТЗ в описании проекта ','in_progress','normal',5,1,'2025-10-31 17:24:00.000000',10,NULL,'2025-10-24 14:25:03.195970','2025-10-27 17:24:51.187847',NULL,'{}','normal',90,0,NULL);
INSERT INTO tasks VALUES(189,'@AlekseyKoroloff - набрать до 15 ноября 2025 года ','@AlekseyKoroloff - набрать до 15 ноября 2025 года - набрать и решить вопрос по боту автобронирование ','pending','normal',1,1,'2025-11-15 11:50:00.000000',NULL,NULL,'2025-10-28 08:51:03.205885','2025-10-28 08:51:03.205889',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(190,'TMA - нейросети ',replace(replace('разработать агрегартор нейросетей в TMA \r\nна сейчас этап делаем backend','\r',char(13)),'\n',char(10)),'in_progress','high',10,1,'2025-11-09 12:36:00.000000',10,NULL,'2025-10-29 09:37:04.408407','2025-11-02 10:49:21.417255',NULL,'{}','green',0,0,'2025-11-02 10:49:21.417171');
INSERT INTO tasks VALUES(194,'Бот контроль ТС - проверить работу','закажичик пишет что бот не работает , надо проверить','pending','normal',3,1,'2025-11-01 16:37:00.000000',1,NULL,'2025-10-31 08:32:12.077369','2025-10-31 08:32:12.077373',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(195,'Боты перевозчику',replace(replace('нужен бот зп , отгрузки с доработками , ужердания \r\n\r\nпавел - ему уже делали остатки ПМ','\r',char(13)),'\n',char(10)),'pending','normal',5,1,'2025-11-08 18:56:00.000000',2,NULL,'2025-11-05 15:56:13.889742','2025-11-06 08:05:44.310150',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(196,'Бот для вотсап - связаться (1677) WA BBUSINEES','связаться сделать договор и отправить счет на оплату ','pending','normal',1,1,'2025-11-06 12:59:00.000000',NULL,NULL,'2025-11-05 16:56:47.162655','2025-11-05 16:56:47.162659',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(197,'Алсу/Лена ИИ продавец закрыть сделку','','pending','normal',1,1,'2025-11-06 12:30:00.000000',NULL,NULL,'2025-11-05 16:59:38.981802','2025-11-05 16:59:38.981806',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(198,'Бот офтальмолог ','у него снова че то сломалось ','in_progress','normal',5,1,'2025-11-08 11:56:00.000000',2,NULL,'2025-11-06 08:57:01.514491','2025-11-08 15:34:46.640661',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(199,'Евгений бот тг Битрикс','Отправить рабочую модель к 14:00','pending','normal',1,1,'2025-11-06 13:30:00.000000',NULL,NULL,'2025-11-06 09:47:33.951564','2025-11-06 09:47:33.951567',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(200,'Лука ТГ БОТ для Пекарни дотянуть',replace(replace('Телеграм бот 15 000\r\nАдминистративная консоль 3 500\r\nСистема уведомлений 2 000\r\nИтого: 20 500','\r',char(13)),'\n',char(10)),'pending','normal',1,1,'2025-11-07 14:00:00.000000',NULL,NULL,'2025-11-06 15:41:52.805924','2025-11-06 15:41:52.805929',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(201,'Бот - вотсап ( автоматический ответчик на сообщения в чате)','сделать бота который будет подлкчен к аккаунту в вотсапе через GREENAPI чтобы реагировал на определенные фразы - отправил тебе в личные сообщения','pending','normal',3,1,'2025-11-14 12:32:00.000000',10,NULL,'2025-11-07 09:32:17.997796','2025-11-07 09:32:17.997800',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(202,'Лука тг Бот ВЫПЕЧКА','Связаться на след неделе, добить сделку','pending','normal',1,1,'2025-11-11 12:00:00.000000',NULL,NULL,'2025-11-07 12:20:13.574494','2025-11-07 12:20:13.574498',NULL,'{}','normal',0,0,NULL);
INSERT INTO tasks VALUES(203,'Пузляш - сделать доступ ЗП к 1 аккаунту','Внедряем ему тест на несколько дней , согласовал паше 10к за страдания в процессе','in_progress','high',5,1,'2025-11-08 16:00:00.000000',10,NULL,'2025-11-07 13:01:04.970529','2025-11-08 15:34:41.280983',NULL,'{}','green',0,0,NULL);
INSERT INTO tasks VALUES(204,'@manage_tech - связаться 12.11 ','обсуждали два проекта по ювелирке и технике над согласовать попросили два дня думать ','pending','normal',1,1,'2025-11-12 13:54:00.000000',10,NULL,'2025-11-10 10:54:14.846104','2025-11-10 10:54:14.846108',NULL,'{}','normal',0,0,NULL);
CREATE TABLE task_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    comment_type VARCHAR(50) NOT NULL DEFAULT 'general',
                    is_internal BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, attachments TEXT, is_read INTEGER DEFAULT 0, read_by TEXT DEFAULT '[]',
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (author_id) REFERENCES admin_users (id)
                );
INSERT INTO task_comments VALUES(25,50,1,'Изменения: цвет: normal → green','status_change',0,'2025-08-04 09:46:44.636696',NULL,1,'[1]');
INSERT INTO task_comments VALUES(68,96,1,'Изменения: цвет: normal → green','status_change',0,'2025-08-22 08:00:28.300793',NULL,1,'[8]');
INSERT INTO task_comments VALUES(74,50,1,'Изменения: цвет: normal → red','status_change',0,'2025-09-14 05:30:59.745871',NULL,1,'[1]');
INSERT INTO task_comments VALUES(76,61,1,'Изменения: цвет: green → red','status_change',0,'2025-09-14 05:31:18.927720',NULL,0,'[]');
INSERT INTO task_comments VALUES(108,170,1,replace(replace('Добрый день! Чтобы кнопки выглядели более эстетично)) придётся что-то либо удалить либо добавить. Добавь пожалуйста PayPal в способ оплаты, тогда будет 6 кнопок, а не 5\r\n\r\nвот еще сообщение от клиента','\r',char(13)),'\n',char(10)),'general',0,'2025-10-21 10:08:32.492034','[]',1,'[5]');
INSERT INTO task_comments VALUES(109,97,1,'Связался 21 октября - пока ответа нет','general',0,'2025-10-21 11:54:36.403036','[]',1,'[8]');
INSERT INTO task_comments VALUES(110,96,1,'На тесте бот','general',0,'2025-10-21 11:54:54.716485','[]',1,'[8]');
INSERT INTO task_comments VALUES(111,61,1,'Ждем правки от клиента на 21 октября','general',0,'2025-10-21 11:57:38.309439','[]',0,'[]');
INSERT INTO task_comments VALUES(113,175,3,'Статус изменен: pending → in_progress','status_change',0,'2025-10-22 06:36:36.758942','[]',1,'[1]');
INSERT INTO task_comments VALUES(114,172,5,'dfkbvdfjhb','general',0,'2025-10-22 08:55:16.666469','[]',1,'[1]');
INSERT INTO task_comments VALUES(115,166,1,'нужна инфа откуда берутся ссылки на зум узнать','general',0,'2025-10-22 09:03:38.953189','[]',1,'[5]');
INSERT INTO task_comments VALUES(117,166,1,replace(replace('Привет \r\nЯ их создала в зуме, эти ссылки постоянные и они не меняются (меняться будут только в январе 2026 году ) \r\n\r\nЯ просто на каждый урок создала конференцию, сделала постоянной ее , он выдал ссылку и все','\r',char(13)),'\n',char(10)),'general',0,'2025-10-22 10:45:27.288067','[]',1,'[5]');
INSERT INTO task_comments VALUES(118,180,1,'привте','general',0,'2025-10-23 07:16:08.576902','[]',1,'[1]');
INSERT INTO task_comments VALUES(119,180,1,'привет','general',0,'2025-10-23 07:16:19.902688','[{"filename": "c9b137af-dee9-4f19-97ae-27179a43d664.png", "original_filename": "ChatGPT Image 22 \u043e\u043a\u0442. 2025 \u0433., 15_18_47.png", "path": "uploads/task_comments/c9b137af-dee9-4f19-97ae-27179a43d664.png", "type": "image", "size": 1442814}]',1,'[1]');
INSERT INTO task_comments VALUES(120,175,3,'Ожидаю данных от клиента','general',0,'2025-10-23 07:17:14.207366','[]',1,'[1]');
INSERT INTO task_comments VALUES(121,180,4,replace(replace('1. Общие — добавить кнопку «Поделиться» для Telegram, WhatsApp, email и других мессенджеров (через navigator.share() или собственное модальное окно).\r\n\r\n2. Товары и карточки — проверить корректность кнопок выбора размера и цвета (прописать недостающие вручную); реализовать редактирование размерных сеток по категориям; отобразить лимит количества фото на товар; унифицировать информацию о возврате (14 дней) и указать невозвратные категории (бельё, купальники, носки, колготки, чулки); исправить дублирование товаров в корзине (увеличивать количество при повторном добавлении); настроить сохранение избранного между сессиями.\r\n\r\n3. Корзина и оформление заказа — убрать автоматическую подстановку размера, товар добавляется только после выбора; исправить отображение бесплатной доставки (только от 3000 ₽); расширить форму адреса (регион, город, улица, дом, строение, квартира, индекс); удалить оплату наличными, оставить только карту/СБП; заменить сообщение после оформления на автоматическое подтверждение; выровнять кнопки «Мои заказы» и «Продолжить покупки»; добавить статусы заказов, уведомления при изменении и поле для трек-номера.\r\n\r\n4. Программа лояльности — убрать надпись «1 балл = 1 рубль»; изменить расчёт (1 балл = 0,10 ₽, максимум 50% оплаты); сделать доступной всем пользователям, не только VIP; добавить начисление — 1 балл за каждые 100 ₽.\r\n\r\n5. Возвраты и поддержка — определить адрес возвратов (тот же ПВЗ или отдельный); уточнить маршрутизацию раздела «Задать вопрос / вернуть товар» (куда направляется и кто обрабатывает); временно скрыть онлайн-чат при отсутствии оператора; скрыть разделы «служба поддержки», «отдел продаж», «пресс-служба».\r\n\r\n6. Контакты и футер — убрать «Ателье» из названия; удалить телефоны и адрес шоурума; оставить email info@billion.ru\r\n, указать просто «Москва», юридический адрес и режим работы «без выходных».\r\n\r\n7. Поиск — исправить поиск по товарам (не реагирует на ввод); добавить кнопку «Поиск/Найти» или иконку в интерфейсе Mini App; обеспечить срабатывание при нажатии Enter на мобильных устройствах.\r\n\r\n8. Админ-панель — предоставить клиенту доступ к backend с возможностью редактирования товаров, описаний, фото и размеров; заменить формулировку на «Клиент ожидает предоставления доступа к административной панели (backend) для тестирования».\r\n\r\n9. Безопасность и персональные данные — проверить соответствие 152-ФЗ; указать, что данные (ФИО, телефон, email, адрес) хранятся на сервере; добавить адрес сервера в политику конфиденциальности; убедиться в наличии защиты от DDoS, взломов и утечек.\r\n\r\n10. Доставка (финальная версия) — полностью исключить доставку через Wildberries и курьеров; заказы поступают в админку или на email info@billion.ru\r\n; менеджер проверяет наличие товара, при отсутствии — делает возврат; подбирает транспортную компанию (СДЭК, Почта и т.д.) и связывается с клиентом по email; на сайте не указывать конкретные службы, бесплатную доставку и оплату при получении; оставить только фразу: «После оформления заказа наш менеджер свяжется с вами по email для уточнения способа доставки.»\r\n\r\n11. Размеры и цвета — проверить наличие вариантов размера и цвета у всех товаров; добавить вручную, где отсутствуют.','\r',char(13)),'\n',char(10)),'general',0,'2025-10-23 07:34:41.822531','[]',1,'[4]');
INSERT INTO task_comments VALUES(123,179,1,'Уточнить инфу по правкам согласовать стоимость и запустить в работу (позже)','general',0,'2025-10-23 08:11:01.121169','[]',1,'[1]');
INSERT INTO task_comments VALUES(124,170,5,'Все по правкам сделал, кинул Надежде на проверку, пока не читала','general',0,'2025-10-23 08:11:17.097682','[]',1,'[5]');
INSERT INTO task_comments VALUES(138,180,1,replace(replace('1.⁠ ⁠Общие — добавить кнопку «Поделиться» для Telegram, WhatsApp, email и других мессенджеров (через navigator.share() или собственное модальное окно). 2. Товары и карточки — проверить корректность кнопок выбора размера и цвета (прописать недостающие вручную); реализовать редактирование размерных сеток по категориям; отобразить лимит количества фото на товар; унифицировать информацию о возврате (14 дней) и указать невозвратные категории (бельё, купальники, чулочно-носочные изделия); исправить дублирование товаров в корзине (увеличивать количество при повторном добавлении); настроить сохранение избранного между сессиями. 3. Корзина и оформление заказа — убрать автоматическую подстановку размера, товар добавляется только после выбора; исправить отображение бесплатной доставки от 3000 ₽); расширить форму адреса (регион, город, улица, дом, строение, квартира, индекс); удалить оплату наличными, оставить только карту/СБП; заменить сообщение после оформления на автоматическое подтверждение; выровнять кнопки «Мои заказы» и «Продолжить покупки»; добавить статусы заказов, уведомления при изменении и поле для трек-номера. 4. Программа лояльности — убрать надпись «1 балл = 1 рубль»; изменить расчёт (1 балл = 0,10 ₽, максимум 50% оплаты); сделать доступной всем пользователям, не только VIP; добавить начисление — 1 балл за каждые 10 ₽. \r\n5.⁠ ⁠Возвраты и поддержка — определить адрес возвратов (тот же ПВЗ или отдельный) мы каждому клиенту при возврате им в наш адрес товара, будем давать адрес по почте в переписке ; уточнить маршрутизацию раздела «Задать вопрос / вернуть товар» (куда направляется и кто обрабатывает) = пусть пишут на почту по любым вопросам: info@rubyon.ru ; временно скрыть онлайн-чат при отсутствии оператора; скрыть разделы «служба поддержки», «отдел продаж», «пресс-служба». 6. Контакты и футер — заменить название «Ателье» на "Rubyon" ; удалить телефоны и адрес шоурума; оставить email info@rubyon.ru, указать просто «Москва», юридический адрес ООО "Маэстро" и режим работы «без выходных». 7. Поиск — исправить поиск по товарам (не реагирует на ввод); добавить кнопку «Поиск/Найти» или иконку в интерфейсе Mini App; обеспечить срабатывание при нажатии Enter на мобильных устройствах. 8. Админ-панель — предоставить клиенту доступ к backend с возможностью редактирования товаров, описаний, фото и размеров; заменить формулировку на «Клиент ожидает предоставления доступа к административной панели (backend) для тестирования». 9. Безопасность и персональные данные — проверить соответствие 152-ФЗ; указать, что данные (ФИО, телефон, email, адрес) хранятся на сервере; добавить адрес сервера в политику конфиденциальности; убедиться в наличии защиты от DDoS, взломов и утечек. 10. Доставка (финальная версия) — полностью исключить доставку через Wildberries и курьеров; заказы поступают в админку или на email info@rubyon.ru; менеджер проверяет наличие товара, при отсутствии — делает возврат; подбирает транспортную компанию (СДЭК, Почта и т.д.) и связывается с клиентом по email; на сайте не указывать конкретные службы доставки, бесплатную доставку и оплату при получении; оставить только фразу: «После оформления заказа наш менеджер свяжется с вами по email или указанному Вами  мобильному телефону для уточнения способа доставки.» 11. Размеры и цвета — проверить наличие вариантов размера и цвета у всех товаров; добавить вручную, где отсутствуют.','\r',char(13)),'\n',char(10)),'general',0,'2025-10-24 09:05:47.135707','[]',1,'[1]');
INSERT INTO task_comments VALUES(139,174,1,replace(replace('Надо добавить  разделе каждого города ,подраздел «Ваши объявления» и он себя включал подразделы, допустим «Квартиры», автомобили. Ну и сделать что бы мы сами в админ панели могли добавить потом , нужную нам категорию . Так же надо подумать куда добавить услуги которые не имеют города определеного, у нас такое бывает. Например «Разработка игр» или еще что то\r\n\r\nТак же надо опередилить куда добавить рекламу маркетплейсов ,','\r',char(13)),'\n',char(10)),'general',0,'2025-10-24 09:18:44.954553','[]',1,'[1]');
INSERT INTO task_comments VALUES(143,166,5,'Так как зум отключил возможность открывать ссылки в браузере, то надо будет запускать саму прогу и делать скрин, поэтому сейчас с этим вожусь, чтобы нормально все открывалось и работало','general',0,'2025-10-25 10:38:04.761983','[]',1,'[5]');
INSERT INTO task_comments VALUES(144,170,1,'тут есть инфа? она утром писала что бот не работает','general',0,'2025-10-25 12:54:39.527689','[]',1,'[1]');
INSERT INTO task_comments VALUES(145,170,5,'Отключился мой сервак домашний, щас пофиксил, работает','general',0,'2025-10-25 20:47:53.721995','[]',1,'[5]');
INSERT INTO task_comments VALUES(146,170,1,'правки новые','general',0,'2025-10-26 09:53:26.560769','[{"filename": "2b45e99f-491c-409c-8d56-171a56b5c0dc.jpg", "original_filename": "telegram-cloud-photo-size-4-6048472095454334003-x.jpg", "path": "uploads/task_comments/2b45e99f-491c-409c-8d56-171a56b5c0dc.jpg", "type": "image", "size": 51952}, {"filename": "6681235a-ff89-4935-9080-9cab51994e39.jpg", "original_filename": "telegram-cloud-photo-size-4-6048850391878798362-y.jpg", "path": "uploads/task_comments/6681235a-ff89-4935-9080-9cab51994e39.jpg", "type": "image", "size": 60547}]',1,'[1]');
INSERT INTO task_comments VALUES(147,170,1,'еще одна','general',0,'2025-10-26 10:08:29.442201','[{"filename": "2299df50-dae3-4fc2-ac91-8d216a9ffc09.jpg", "original_filename": "telegram-cloud-photo-size-4-6048850391878798367-y.jpg", "path": "uploads/task_comments/2299df50-dae3-4fc2-ac91-8d216a9ffc09.jpg", "type": "image", "size": 37252}]',1,'[1]');
INSERT INTO task_comments VALUES(148,185,1,replace(replace('КРАТКОЕ ТЗ: Telegram-бот для продажи доступа к закрытым каналам\r\nСуть проекта:\r\nНужен бот для монетизации закрытых каналов. Пользователи оплачивают подписку и получают доступ к закрытым группам. Плюс автопродление и возможность платить как из России, так и из-за границы.\r\nСтруктура каналов:\r\n\r\n3 основных канала с платным доступом к закрытым группам\r\nКанал 4 - VIP-наставничество (только оплата, без доступа к группе)\r\nКанал 5 - Индивидуальные консультации (только оплата, дальше связь с консультантом)\r\n\r\nТарифы подписки:\r\n\r\n1 месяц (базовая цена)\r\n6 месяцев (со скидкой)\r\n1 год (со скидкой)\r\nПробного периода не будет\r\n\r\nИнтерфейс бота:\r\nГлавное меню:\r\n\r\n5 кнопок с описанием каналов (можно добавить картинки как в примере)\r\nПри нажатии показывается описание канала и кнопки оплаты (1 месяц / 6 месяцев / 1 год)\r\n\r\nПрофиль пользователя:\r\n\r\nUser ID\r\nАктивные подписки (какой канал и до какого числа)\r\nКнопка включения/выключения автопродления для каждого канала\r\n\r\nЛогика выдачи доступа:\r\nКаналы 1-3: После оплаты пользователь получает доступ к закрытой группе.\r\nТут есть варианты реализации:\r\n\r\nВариант A: Индивидуальная скрытая ссылка (если бот может подменять/подставлять ссылки)\r\nВариант B: Просто выдается обычная ссылка\r\nВариант C: Пользователя автоматически добавляют в группу\r\n\r\nКаналы 4-5: Только оплата, без доступа к группам. После оплаты устанавливается связь с консультантом, который назначает время и дальше работают индивидуально.\r\nПлатежная система:\r\nОсновной вариант - Prodamus (они дешевле при подсчете всех комиссий, чем та же Юкасса).\r\n\r\nПринимает платежи из России\r\nПринимает платежи из-за границы (Казахстан, Грузия, Армения и т.д.)\r\nВ боте нужно добавить выбор: "Вы находитесь в России или за границей?" - чтобы направлять на нужную платежную систему\r\n\r\nАвтопродление подписки:\r\n\r\nАвтоматическое списание средств с привязанной банковской карты\r\nВключение/выключение в профиле пользователя\r\nПока не до конца понятен момент реализации автопродления, нужна консультация как это технически делается\r\n\r\nВеб-админка:\r\nВеб-интерфейс с таблицей статистики:\r\n\r\nКто подключен\r\nК каким каналам\r\nДо какого числа подписка\r\nИстория платежей от каждого пользователя\r\nОбщая статистическая информация\r\n\r\nДополнительные запросы:\r\n\r\nПосмотреть примеры реализации в ваших готовых ботах (скриншоты)\r\nВарианты улучшения интерфейса и менюшек\r\nРекомендации по логике выдачи доступа\r\nРазъяснение механики автопродления','\r',char(13)),'\n',char(10)),'general',0,'2025-10-27 15:45:48.764860','[]',1,'[1]');
INSERT INTO task_comments VALUES(149,185,1,'Кнопка консультатация - название консультация и наставничество переводит в личные сообщения( не оплата)','general',0,'2025-10-27 15:46:12.576833','[]',1,'[1]');
INSERT INTO task_comments VALUES(150,185,5,'Все готово, нужны реальные данные, сервак для подлкючения, настройки и теста','general',0,'2025-10-27 17:25:36.082292','[]',1,'[1]');
INSERT INTO task_comments VALUES(151,185,5,replace(replace('Платежи с автоподпиской работают по рекуретным платежам - встроенная функция в продамус\r\nТакже вопрос: нужна ли функция с включением и отключением продаж и нужна ли страница для догонялок','\r',char(13)),'\n',char(10)),'general',0,'2025-10-27 17:26:56.702700','[]',1,'[1]');
INSERT INTO task_comments VALUES(152,175,3,'ТГ id для админ панели узнать у заказчика! Удобная админ панель для управления курсом добавления, удаление, редактирование уроков, готово ждет id','general',0,'2025-10-28 07:45:29.633782','[]',1,'[1]');
INSERT INTO task_comments VALUES(153,175,3,'По Lava на сайте требует добавить платный контент для добавления продукта, продукт нам нужен для создания платежек с покупкой всего курса со скидкой.','general',0,'2025-10-28 08:00:30.947120','[]',1,'[1]');
INSERT INTO task_comments VALUES(154,176,8,'Готов к тестам, нужны реальные сценарии работы','general',0,'2025-10-28 20:11:18.785908','[]',1,'[1]');
INSERT INTO task_comments VALUES(156,96,8,'Внес исправления, жду повторного тестирования','general',0,'2025-10-28 20:14:16.267602','[]',1,'[8]');
INSERT INTO task_comments VALUES(157,185,1,'Информацию передал, жду информацию','general',0,'2025-10-29 07:34:00.034717','[]',1,'[1]');
INSERT INTO task_comments VALUES(160,185,1,'Бота моешь размещать на моем серваке - данные от сервера кинь сюда','general',0,'2025-10-29 08:25:56.598021','[]',1,'[1]');
INSERT INTO task_comments VALUES(161,172,1,'по этому боту заказчику нужно показать промежуточный результат - жду инфо в лс','general',0,'2025-10-29 08:26:34.333569','[]',1,'[1]');
INSERT INTO task_comments VALUES(162,171,1,'по этому получилось все? комментариев нет','general',0,'2025-10-29 08:27:00.425503','[]',1,'[1]');
INSERT INTO task_comments VALUES(163,170,1,'Тут также жду инфо на каком этапе','general',0,'2025-10-29 08:27:25.881351','[]',1,'[1]');
INSERT INTO task_comments VALUES(164,169,1,'Ждем инфо)','general',0,'2025-10-29 08:27:40.208868','[]',1,'[1]');
INSERT INTO task_comments VALUES(166,166,1,'Тут есть продвижки?','general',0,'2025-10-29 08:28:46.371217','[]',1,'[1]');
INSERT INTO task_comments VALUES(167,174,1,'На сейчас сделали фронт - делаем бекенд и внедряем функции автозагрузки видосов с TIKTOK','general',0,'2025-10-29 08:31:02.620694','[]',1,'[1]');
INSERT INTO task_comments VALUES(169,176,1,replace(replace('С ним решаем он не выыходит на связь, ищу потенциальных клиентов на данную разарботку, готов оплатить работу \r\n\r\nв дальнейшем надо будет доработать под клиента','\r',char(13)),'\n',char(10)),'general',0,'2025-10-29 08:34:27.304601','[]',1,'[1]');
INSERT INTO task_comments VALUES(170,175,1,'еще одну функцию надо','general',0,'2025-10-29 10:46:44.863003','[{"filename": "58539fa3-b1b4-40f4-9644-1a16e18d8d13.png", "original_filename": "image.png", "path": "uploads/task_comments/58539fa3-b1b4-40f4-9644-1a16e18d8d13.png", "type": "image", "size": 1026562}]',1,'[1]');
INSERT INTO task_comments VALUES(171,171,5,'по этому инфы не было никакой, если этот тот, у которого токены менять, то он сервак делает','general',0,'2025-10-29 11:38:56.381245','[]',1,'[5]');
INSERT INTO task_comments VALUES(172,170,5,'На связи с ней, жду от нее инфы, так как все правки сделанны','general',0,'2025-10-29 11:39:46.358446','[]',1,'[5]');
INSERT INTO task_comments VALUES(175,185,1,'что делать?','general',0,'2025-10-30 07:05:09.502661','[{"filename": "a08aad0e-9e28-4046-94f9-929272d01777.png", "original_filename": "image.png", "path": "uploads/task_comments/a08aad0e-9e28-4046-94f9-929272d01777.png", "type": "image", "size": 345666}]',1,'[1]');
INSERT INTO task_comments VALUES(176,185,1,replace(replace('https://drive.google.com/file/d/1npwJPa672b4XcFsZcLytuTYMruovjTgY/view?usp=sharing\r\nдобавить в бот ссылку на оферту','\r',char(13)),'\n',char(10)),'general',0,'2025-10-30 07:07:04.754235','[]',1,'[1]');
INSERT INTO task_comments VALUES(177,185,1,'точнее не ссылку а гиперссылку на слово оферта','general',0,'2025-10-30 07:07:33.962407','[]',1,'[1]');
INSERT INTO task_comments VALUES(180,170,1,'правки','general',0,'2025-10-30 09:32:45.681730','[{"filename": "198fabbe-594f-4787-88ac-efafa55b67c8.png", "original_filename": "image.png", "path": "uploads/task_comments/198fabbe-594f-4787-88ac-efafa55b67c8.png", "type": "image", "size": 1073508}]',1,'[1]');
INSERT INTO task_comments VALUES(182,185,5,replace(replace('@kde456_test_bot бот\r\nhttp://82.147.71.210/ админка \r\nлогин: admin@ya.ru\r\nпароль: admin4321','\r',char(13)),'\n',char(10)),'general',0,'2025-10-30 14:09:42.410751','[]',1,'[5]');
INSERT INTO task_comments VALUES(183,185,1,'отправил на проверку','general',0,'2025-10-30 16:09:31.488256','[]',1,'[1]');
INSERT INTO task_comments VALUES(184,185,1,'правки','general',0,'2025-10-30 16:55:33.714286','[{"filename": "04cd5233-7ef7-42c4-8179-063030c8b192.png", "original_filename": "image.png", "path": "uploads/task_comments/04cd5233-7ef7-42c4-8179-063030c8b192.png", "type": "image", "size": 616715}]',1,'[1]');
INSERT INTO task_comments VALUES(185,185,5,'Внес правкм','general',0,'2025-10-30 17:52:03.619635','[]',1,'[5]');
INSERT INTO task_comments VALUES(186,185,1,'правки #2','general',0,'2025-10-31 08:26:45.173882','[{"filename": "220e4b64-6b62-44c5-889e-3975070cd46b.png", "original_filename": "image.png", "path": "uploads/task_comments/220e4b64-6b62-44c5-889e-3975070cd46b.png", "type": "image", "size": 1637761}, {"filename": "5797e6f9-3ab9-4967-b11e-82164bca1cbc.png", "original_filename": "image.png", "path": "uploads/task_comments/5797e6f9-3ab9-4967-b11e-82164bca1cbc.png", "type": "image", "size": 1518850}, {"filename": "9231bf56-7d57-4429-89f8-82c954de80f9.png", "original_filename": "image.png", "path": "uploads/task_comments/9231bf56-7d57-4429-89f8-82c954de80f9.png", "type": "image", "size": 1163890}, {"filename": "dbbd1add-9b96-4f33-bb40-5295358e0372.png", "original_filename": "image.png", "path": "uploads/task_comments/dbbd1add-9b96-4f33-bb40-5295358e0372.png", "type": "image", "size": 1110137}, {"filename": "477be229-1631-440f-b1d7-bda06e1b58f3.png", "original_filename": "image.png", "path": "uploads/task_comments/477be229-1631-440f-b1d7-bda06e1b58f3.png", "type": "image", "size": 1139347}]',1,'[1]');
INSERT INTO task_comments VALUES(190,185,5,'Попроси этой юзернейм @OKTOPAMA в трёх группах сделать админом','general',0,'2025-10-31 08:41:29.044212','[]',1,'[5]');
INSERT INTO task_comments VALUES(191,185,5,'Попроси этой юзернейм @OKTOPAMA в трёх группах сделать админом','general',0,'2025-10-31 08:41:29.886793','[]',1,'[5]');
INSERT INTO task_comments VALUES(192,185,5,'Попроси этой юзернейм @OKTOPAMA в трёх группах сделать админом','general',0,'2025-10-31 08:41:30.267269','[]',1,'[5]');
INSERT INTO task_comments VALUES(193,185,5,'Попроси этой юзернейм @OKTOPAMA в трёх группах сделать админом','general',0,'2025-10-31 08:41:30.681837','[]',1,'[5]');
INSERT INTO task_comments VALUES(194,185,5,'Попроси этой юзернейм @OKTOPAMA в трёх группах сделать админом','general',0,'2025-10-31 08:41:31.113716','[]',1,'[5]');
INSERT INTO task_comments VALUES(195,185,1,'сделать кнопку в лк для отключения автоплатежа ( автоплатеж должен включаться автоматически)','general',0,'2025-10-31 08:48:37.519439','[]',1,'[1]');
INSERT INTO task_comments VALUES(196,172,1,'обрати внимание - нужен твой комментарий','general',0,'2025-10-31 09:10:29.617619','[{"filename": "ce8bb5be-c3a3-4c4f-9382-88b8a7edba6f.png", "original_filename": "image.png", "path": "uploads/task_comments/ce8bb5be-c3a3-4c4f-9382-88b8a7edba6f.png", "type": "image", "size": 1279761}]',1,'[1]');
INSERT INTO task_comments VALUES(198,172,5,'Принял, в ближайшее время дам связь, на серваке тестирую','general',0,'2025-10-31 09:21:25.349075','[]',1,'[5]');
INSERT INTO task_comments VALUES(199,185,5,replace(replace('@quantumfields_bot\r\nдля настройки конечной автоплатежей, нужен будет уже продамус действующий. В нем создается подписка с рекурентным платежом, пользователь после первой оплаты осуществляет подписку, через личный кабинет может отменить подписку. Сейчас настроено уведомление за сутки до конца подписки, конец подписки считается ровно не в конец суток (24:00), а в то время, в которое оплатил пользователь. Подписку также сможет отменять менеджер через саму систему продамус','\r',char(13)),'\n',char(10)),'general',0,'2025-10-31 13:49:20.819332','[]',1,'[5]');
INSERT INTO task_comments VALUES(200,185,5,replace(replace('@quantumfields_bot\r\nдля настройки конечной автоплатежей, нужен будет уже продамус действующий. В нем создается подписка с рекурентным платежом, пользователь после первой оплаты осуществляет подписку, через личный кабинет может отменить подписку. Сейчас настроено уведомление за сутки до конца подписки, конец подписки считается ровно не в конец суток (24:00), а в то время, в которое оплатил пользователь. Подписку также сможет отменять менеджер через саму систему продамус','\r',char(13)),'\n',char(10)),'general',0,'2025-10-31 13:49:21.281658','[]',1,'[5]');
INSERT INTO task_comments VALUES(201,172,5,replace(replace('@salary_adminbot\r\nадмин панель - http://83.147.247.81:3000/admin/waysheets\r\nрасчитывается в админ панели через путевые листы, также в телеграм боте это есть','\r',char(13)),'\n',char(10)),'general',0,'2025-10-31 13:52:34.614845','[]',1,'[5]');
INSERT INTO task_comments VALUES(206,170,1,'правки внесены связаться с клиентом чтобы он подтвердил','general',0,'2025-11-02 10:10:43.026091','[]',1,'[1]');
INSERT INTO task_comments VALUES(207,172,1,'Ваня отправить клиенту на согласование + Паша сделть подробную инструкуцию по использованию бота','general',0,'2025-11-02 10:11:31.829346','[]',1,'[1]');
INSERT INTO task_comments VALUES(209,171,1,'дать админку','general',0,'2025-11-02 10:20:31.560620','[{"filename": "31e9100c-259c-4ee3-aab1-13d9258d3895.png", "original_filename": "image.png", "path": "uploads/task_comments/31e9100c-259c-4ee3-aab1-13d9258d3895.png", "type": "image", "size": 175829}]',1,'[1]');
INSERT INTO task_comments VALUES(210,171,1,'https://t.me/+7mai0jMAk74zOWY1','general',0,'2025-11-02 10:20:42.482360','[]',1,'[1]');
INSERT INTO task_comments VALUES(211,172,1,replace(replace('Созвонился с клиентом - все понравилось есть мелкие правки \r\nсегодня - завтра отправит оплату \r\n\r\nнадо его закрывать','\r',char(13)),'\n',char(10)),'general',0,'2025-11-06 08:33:57.108327','[]',1,'[1]');
INSERT INTO task_comments VALUES(212,96,1,'Уточни по апи МАКС - надо ему ответ дать','general',0,'2025-11-06 08:49:36.793446','[]',1,'[1]');
INSERT INTO task_comments VALUES(213,97,1,'Она не на связи - платить не хочет','general',0,'2025-11-06 08:49:55.579305','[]',1,'[1]');
INSERT INTO task_comments VALUES(214,198,1,'вот','general',0,'2025-11-06 08:57:11.398562','[{"filename": "65ad35cf-5e1f-46c6-b16e-221dfac80f0e.png", "original_filename": "image.png", "path": "uploads/task_comments/65ad35cf-5e1f-46c6-b16e-221dfac80f0e.png", "type": "image", "size": 78518}]',1,'[1]');
INSERT INTO task_comments VALUES(215,175,1,'Отправил на согласование добавление функции оплаты в разных валютах','general',0,'2025-11-06 09:01:22.761523','[]',1,'[1]');
INSERT INTO task_comments VALUES(216,175,1,replace(replace('Добавление валютных оплат + 6500 согласовал \r\nдобавление оплаты криптой + 5000 \r\n\r\nнадо ссылку на сервис который принимает платежи в крипте','\r',char(13)),'\n',char(10)),'general',0,'2025-11-06 09:04:49.902518','[]',1,'[1]');
INSERT INTO task_comments VALUES(217,179,1,'надо ответ ей','general',0,'2025-11-06 09:05:20.619468','[{"filename": "d9af730e-59cb-42fa-a9a5-48d081e5c187.png", "original_filename": "image.png", "path": "uploads/task_comments/d9af730e-59cb-42fa-a9a5-48d081e5c187.png", "type": "image", "size": 480363}]',1,'[1]');
INSERT INTO task_comments VALUES(218,198,5,'Запрос отзыва и оценки работает','general',0,'2025-11-06 09:06:16.005116','[{"filename": "4a847dc4-62c3-4002-a30c-ab4057b9e246.png", "original_filename": "Screenshot_20251106-120440.png", "path": "uploads/task_comments/4a847dc4-62c3-4002-a30c-ab4057b9e246.png", "type": "image", "size": 97477}]',1,'[5]');
INSERT INTO task_comments VALUES(219,201,1,replace(replace('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\r\nключ опенапи','\r',char(13)),'\n',char(10)),'general',0,'2025-11-07 09:32:58.416235','[]',1,'[1]');
INSERT INTO task_comments VALUES(220,201,3,'Бот функцию отрабатывает предлагаю пригласить заказчика в группу что бы он посмотрел результат сам потестировал его, бот игнорирует сообщения со словами исключениями и пишут беру на те что подходят под заданные параметры','general',0,'2025-11-07 11:40:21.771454','[{"filename": "deff521f-5611-416f-9c01-6f07e9e2b3eb.png", "original_filename": "image.png", "path": "uploads/task_comments/deff521f-5611-416f-9c01-6f07e9e2b3eb.png", "type": "image", "size": 695461}]',1,'[3]');
INSERT INTO task_comments VALUES(221,179,1,replace(replace('Согласовал увеличение бюджета на 50к\r\nвнедряем историю как в авито + админ консоль для модерации','\r',char(13)),'\n',char(10)),'general',0,'2025-11-07 12:59:54.723026','[]',1,'[1]');
INSERT INTO task_comments VALUES(222,179,1,'вот','general',0,'2025-11-07 13:00:02.267268','[{"filename": "446fda0e-7292-442c-96f7-e1bb09596cc5.png", "original_filename": "image.png", "path": "uploads/task_comments/446fda0e-7292-442c-96f7-e1bb09596cc5.png", "type": "image", "size": 227745}]',1,'[1]');
INSERT INTO task_comments VALUES(223,203,5,replace(replace('@test_terehov_bot\r\n\r\nhttp://195.80.51.19:3000/admin/drivers','\r',char(13)),'\n',char(10)),'general',0,'2025-11-07 13:50:40.889629','[]',1,'[5]');
INSERT INTO task_comments VALUES(224,203,1,'на тесте!','general',0,'2025-11-07 21:25:59.225411','[]',1,'[1]');
INSERT INTO task_comments VALUES(225,195,5,'Этому делать зп или пока ждем точных указаний?','general',0,'2025-11-08 10:28:33.025837','[]',1,'[5]');
INSERT INTO task_comments VALUES(227,172,1,'не открывается','general',0,'2025-11-10 11:07:57.586786','[{"filename": "4c0a6036-587f-4224-8ec1-28a8f0ecdadb.png", "original_filename": "image.png", "path": "uploads/task_comments/4c0a6036-587f-4224-8ec1-28a8f0ecdadb.png", "type": "image", "size": 257725}]',1,'[1]');
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
INSERT INTO receipt_files VALUES(1,'receipt_501613334_1754254464.jpg','receipt_501613334_1754254464.jpg','uploads/receipts/receipt_501613334_1754254464.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.29999999999999998889,NULL,NULL,'2025-08-03 20:54:25.665755','2025-08-03 20:54:25.664995',1);
INSERT INTO receipt_files VALUES(2,'receipt_501613334_1754254767.jpg','receipt_501613334_1754254767.jpg','uploads/receipts/receipt_501613334_1754254767.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.29999999999999998889,NULL,NULL,'2025-08-03 20:59:28.490495','2025-08-03 20:59:28.490233',1);
INSERT INTO receipt_files VALUES(3,'receipt_501613334_1754255123.jpg','receipt_501613334_1754255123.jpg','uploads/receipts/receipt_501613334_1754255123.jpg',59737,'jpg','completed','{"success": true, "raw_text": "zon 6aHk\n\nozonbank_document_20250803235259.pdf\n\nozon 6aHK\n\n25 000 P\n\nCratyc YeneuwiHo:\nCy\u00e9r 3auncnenna OcHosHoi cu\u00e9T\nCymma 25 000 P\nKomuccua Bes komuccuu\nOtnpasutenb Bnagumup AnexcaHgposus J1.\n\nTenecbou otnpasurena 47 (926) 000-02-25\n\n8 (800) 555-89-82\n\nNonenuteca\n\n", "amount": null, "date": null, "confidence": 0.3, "extracted_amounts": [], "extracted_dates": []}',0.29999999999999998889,NULL,NULL,'2025-08-03 21:05:24.503022','2025-08-03 21:05:24.502330',1);
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
CREATE TABLE admin_activity_logs (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	action VARCHAR(100) NOT NULL, 
	action_type VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id INTEGER, 
	details JSON, 
	ip_address VARCHAR(50), 
	user_agent VARCHAR(500), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES admin_users (id)
);
CREATE TABLE transactions (
	id INTEGER NOT NULL, 
	transaction_type VARCHAR(20) NOT NULL, 
	project_id INTEGER, 
	contractor_id INTEGER, 
	user_id INTEGER, 
	amount FLOAT NOT NULL, 
	currency VARCHAR(10), 
	category VARCHAR(100), 
	subcategory VARCHAR(100), 
	description TEXT, 
	payment_method VARCHAR(50), 
	reference_number VARCHAR(100), 
	status VARCHAR(20), 
	transaction_date DATETIME NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	transaction_metadata JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(contractor_id) REFERENCES admin_users (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(created_by_id) REFERENCES admin_users (id)
);
INSERT INTO transactions VALUES(1,'income',1,NULL,10,80000.0,'RUB','Оплата проекта',NULL,'Оплата по проекту','bank',NULL,'completed','2025-08-22 08:52:53.437000','2025-08-22 08:52:53.651517','2025-08-22 08:52:53.651525',1,'{}');
INSERT INTO transactions VALUES(2,'income',5,NULL,23,10000.0,'RUB','Оплата проекта',NULL,'предоплата ','карта ',NULL,'completed','2025-09-03 08:17:42.633000','2025-09-03 08:17:42.958658','2025-09-03 08:17:42.958662',1,'{}');
INSERT INTO transactions VALUES(3,'income',3,NULL,22,150000.0,'RUB','Оплата проекта',NULL,'проект полностью оплачен','карта ',NULL,'completed','2025-09-03 08:19:43.068000','2025-09-03 08:19:43.372806','2025-09-03 08:19:43.372809',1,'{}');
INSERT INTO transactions VALUES(4,'income',9,NULL,23,90000.0,'RUB','Оплата проекта',NULL,'предоплата','рассчетный счет Николая ',NULL,'completed','2025-09-03 08:24:46.744000','2025-09-03 08:24:46.954714','2025-09-03 08:24:46.954719',1,'{}');
INSERT INTO transactions VALUES(5,'income',7,NULL,23,40000.0,'RUB','Оплата проекта',NULL,'предоплата ','карта',NULL,'completed','2025-09-03 08:25:30.695000','2025-09-03 08:25:31.181982','2025-09-03 08:25:31.181986',1,'{}');
INSERT INTO transactions VALUES(6,'income',11,NULL,23,50000.0,'RUB','Оплата проекта',NULL,'проект полность/ оплачен','карта',NULL,'completed','2025-09-03 08:26:05.263000','2025-09-03 08:26:05.546647','2025-09-03 08:26:05.546650',1,'{}');
INSERT INTO transactions VALUES(7,'income',17,NULL,23,127499.99999999999999,'RUB','Оплата проекта',NULL,'оплата проекта полность/','акак',NULL,'completed','2025-09-03 08:46:10.335000','2025-09-03 08:46:10.623471','2025-09-03 08:46:10.623475',1,'{}');
INSERT INTO transactions VALUES(8,'income',13,NULL,23,15000.0,'RUB','Оплата проекта',NULL,'оплата проекта','карта',NULL,'completed','2025-09-29 08:02:57.020000','2025-09-29 08:02:57.236362','2025-09-29 08:02:57.236365',1,'{}');
INSERT INTO transactions VALUES(9,'income',22,NULL,36,200000.0,'RUB','Оплата проекта',NULL,'оплата всего проекта','рассчетный счет',NULL,'completed','2025-09-29 08:04:00.584000','2025-09-29 08:04:00.789117','2025-09-29 08:04:00.789121',1,'{}');
CREATE TABLE expense_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	color VARCHAR(20), 
	icon VARCHAR(50), 
	is_active BOOLEAN, 
	order_index INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        type VARCHAR(20) DEFAULT 'individual',
        status VARCHAR(20) DEFAULT 'new',
        phone VARCHAR(50),
        email VARCHAR(255),
        telegram VARCHAR(100),
        whatsapp VARCHAR(50),
        website VARCHAR(500),
        address TEXT,
        company_name VARCHAR(500),
        inn VARCHAR(20),
        kpp VARCHAR(20),
        ogrn VARCHAR(20),
        bank_details JSON,
        source VARCHAR(100),
        description TEXT,
        preferences JSON,
        communication_history JSON DEFAULT '[]',
        total_revenue REAL DEFAULT 0.0,
        average_check REAL DEFAULT 0.0,
        payment_terms VARCHAR(200),
        credit_limit REAL,
        rating INTEGER DEFAULT 0,
        segment VARCHAR(50),
        loyalty_level VARCHAR(50),
        manager_id INTEGER,
        telegram_user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER, avito_chat_id TEXT, avito_user_id TEXT, avito_status TEXT, avito_dialog_history TEXT, avito_notes TEXT, avito_follow_up TEXT,
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (telegram_user_id) REFERENCES users(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    );
INSERT INTO clients VALUES(1,'Nikolaev Telegram Bots & Mini Apps','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'avito_241900337',replace('Объявление: Создам чат бота Telegram любой функционал\n\nСводка диалога:\n1. Клиент интересуется разработкой ботов для двух проектов: парсера объявлений на Авито с уведомлениями в Telegram и бота для автозабронировки на Wildberries.\n2. Услуги включают создание Telegram-бота для парсинга, уведомлений, онлайн-записи и интеграции с CRM-системами.\n3. Бюджет составляет до 100,000 рублей для бота автосервиса и 50-60 тыс. рублей для парсера на Авито.\n4. Клиент готов к покупке, обсуждая детали и функционал проектов.\n5. Договоренности включают реализацию минимального функционала в ограниченные сроки и возможность параллельной разработки с командой клиента.\n6. Следующие шаги — уточнение требований к функционалу, обсуждение сроков и деталей проекта, а также определение приоритетов в задачах для ботов.','\n',char(10)),'{"interests": "1. \u041a\u043b\u0438\u0435\u043d\u0442 \u0438\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442\u0441\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u043e\u0439 \u0431\u043e\u0442\u043e\u0432 \u0434\u043b\u044f \u0434\u0432\u0443\u0445 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432: \u043f\u0430\u0440\u0441\u0435\u0440\u0430 \u043e\u0431\u044a\u044f\u0432\u043b\u0435\u043d\u0438\u0439 \u043d\u0430 \u0410\u0432\u0438\u0442\u043e \u0441 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u0432 Telegram \u0438 \u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u0430\u0432\u0442\u043e\u0437\u0430\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u043a\u0438 \u043d\u0430 Wildberries.\n2. \u0423\u0441\u043b\u0443\u0433\u0438 \u0432\u043a\u043b\u044e\u0447\u0430\u044e\u0442 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 Telegram-\u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u043f\u0430\u0440\u0441\u0438\u043d\u0433\u0430, \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0439, \u043e\u043d\u043b\u0430\u0439\u043d-\u0437\u0430\u043f\u0438\u0441\u0438 \u0438 \u0438\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u0438 \u0441 CRM-\u0441\u0438\u0441\u0442\u0435\u043c\u0430\u043c\u0438.\n3. \u0411\u044e\u0434\u0436\u0435\u0442 \u0441\u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0435\u0442 \u0434\u043e 100,000 \u0440\u0443\u0431\u043b\u0435\u0439 \u0434\u043b\u044f \u0431\u043e\u0442\u0430 \u0430\u0432\u0442\u043e\u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u0438 50-60 \u0442\u044b\u0441. \u0440\u0443\u0431\u043b\u0435\u0439 \u0434\u043b\u044f \u043f\u0430\u0440\u0441\u0435\u0440\u0430 \u043d\u0430 \u0410\u0432\u0438\u0442\u043e.\n4. \u041a\u043b\u0438\u0435\u043d\u0442 \u0433\u043e\u0442\u043e\u0432 \u043a \u043f\u043e\u043a\u0443\u043f\u043a\u0435, \u043e\u0431\u0441\u0443\u0436\u0434\u0430\u044f \u0434\u0435\u0442\u0430\u043b\u0438 \u0438 \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432.\n5. \u0414\u043e\u0433\u043e\u0432\u043e\u0440\u0435\u043d\u043d\u043e\u0441\u0442\u0438 \u0432\u043a\u043b\u044e\u0447\u0430\u044e\u0442 \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044e \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u0430 \u0432 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u043d\u044b\u0435 \u0441\u0440\u043e\u043a\u0438 \u0438 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c\u043d\u043e\u0439 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0441 \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 \u043a\u043b\u0438\u0435\u043d\u0442\u0430.\n6. \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0435 \u0448\u0430\u0433\u0438 \u2014 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u0439 \u043a \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u0443, \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u0435 \u0441\u0440\u043e\u043a\u043e\u0432 \u0438 \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u043f\u0440\u043e\u0435\u043a\u0442\u0430, \u0430 \u0442\u0430\u043a\u0436\u0435 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442\u043e\u0432 \u0432 \u0437\u0430\u0434\u0430\u0447\u0430\u0445 \u0434\u043b\u044f \u0431\u043e\u0442\u043e\u0432.", "budget_mentioned": true}','[{"date": "2025-08-23T11:32:45.252799", "channel": "avito", "summary": "1. \u041a\u043b\u0438\u0435\u043d\u0442 \u0438\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442\u0441\u044f \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u043e\u0439 \u0431\u043e\u0442\u043e\u0432 \u0434\u043b\u044f \u0434\u0432\u0443\u0445 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432: \u043f\u0430\u0440\u0441\u0435\u0440\u0430 \u043e\u0431\u044a\u044f\u0432\u043b\u0435\u043d\u0438\u0439 \u043d\u0430 \u0410\u0432\u0438\u0442\u043e \u0441 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u0432 Telegram \u0438 \u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u0430\u0432\u0442\u043e\u0437\u0430\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u043a\u0438 \u043d\u0430 Wildberries.\n2. \u0423\u0441\u043b\u0443\u0433\u0438 \u0432\u043a\u043b\u044e\u0447\u0430\u044e\u0442 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 Telegram-\u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u043f\u0430\u0440\u0441\u0438\u043d\u0433\u0430, \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0439, \u043e\u043d\u043b\u0430\u0439\u043d-\u0437\u0430\u043f\u0438\u0441\u0438 \u0438 \u0438\u043d\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u0438 \u0441 CRM-\u0441\u0438\u0441\u0442\u0435\u043c\u0430\u043c\u0438.\n3. \u0411\u044e\u0434\u0436\u0435\u0442 \u0441\u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0435\u0442 \u0434\u043e 100,000 \u0440\u0443\u0431\u043b\u0435\u0439 \u0434\u043b\u044f \u0431\u043e\u0442\u0430 \u0430\u0432\u0442\u043e\u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u0438 50-60 \u0442\u044b\u0441. \u0440\u0443\u0431\u043b\u0435\u0439 \u0434\u043b\u044f \u043f\u0430\u0440\u0441\u0435\u0440\u0430 \u043d\u0430 \u0410\u0432\u0438\u0442\u043e.\n4. \u041a\u043b\u0438\u0435\u043d\u0442 \u0433\u043e\u0442\u043e\u0432 \u043a \u043f\u043e\u043a\u0443\u043f\u043a\u0435, \u043e\u0431\u0441\u0443\u0436\u0434\u0430\u044f \u0434\u0435\u0442\u0430\u043b\u0438 \u0438 \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432.\n5. \u0414\u043e\u0433\u043e\u0432\u043e\u0440\u0435\u043d\u043d\u043e\u0441\u0442\u0438 \u0432\u043a\u043b\u044e\u0447\u0430\u044e\u0442 \u0440\u0435\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044e \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u0430 \u0432 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u043d\u044b\u0435 \u0441\u0440\u043e\u043a\u0438 \u0438 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c\u043d\u043e\u0439 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0441 \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 \u043a\u043b\u0438\u0435\u043d\u0442\u0430.\n6. \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0435 \u0448\u0430\u0433\u0438 \u2014 \u0443\u0442\u043e\u0447\u043d\u0435\u043d\u0438\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u0439 \u043a \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u0443, \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u0435 \u0441\u0440\u043e\u043a\u043e\u0432 \u0438 \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u043f\u0440\u043e\u0435\u043a\u0442\u0430, \u0430 \u0442\u0430\u043a\u0436\u0435 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442\u043e\u0432 \u0432 \u0437\u0430\u0434\u0430\u0447\u0430\u0445 \u0434\u043b\u044f \u0431\u043e\u0442\u043e\u0432.", "chat_id": "u2i-zDw44NhFRU~HmbPT5YQSiQ"}]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-08-23 08:32:45.257338','2025-08-23 08:32:45.257343',1,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO clients VALUES(2,'Анна','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'avito_69681716',replace('Объявление: Создам Telegram бот и Mini App Готово за 1 день\n\nСводка диалога:\n1. Клиент спрашивал о создании телеграмм бота для автоматизированной продажи угля.\n2. Интересует услуга разработки телеграмм бота или мини приложения.\n3. Бюджет не упоминался.\n4. Клиент готов к сотрудничеству и спрашивает о помощи в составлении технического задания.\n5. Продавец предложил созвониться для обсуждения деталей проекта.\n6. Следующий шаг — телефонный звонок для более детального обсуждения.','\n',char(10)),'{"interests": "1. \u041a\u043b\u0438\u0435\u043d\u0442 \u0441\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u043b \u043e \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0438 \u0442\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c \u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0434\u0430\u0436\u0438 \u0443\u0433\u043b\u044f.\n2. \u0418\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442 \u0443\u0441\u043b\u0443\u0433\u0430 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0442\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c \u0431\u043e\u0442\u0430 \u0438\u043b\u0438 \u043c\u0438\u043d\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f.\n3. \u0411\u044e\u0434\u0436\u0435\u0442 \u043d\u0435 \u0443\u043f\u043e\u043c\u0438\u043d\u0430\u043b\u0441\u044f.\n4. \u041a\u043b\u0438\u0435\u043d\u0442 \u0433\u043e\u0442\u043e\u0432 \u043a \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u0447\u0435\u0441\u0442\u0432\u0443 \u0438 \u0441\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043e \u043f\u043e\u043c\u043e\u0449\u0438 \u0432 \u0441\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u0438\u0438 \u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0437\u0430\u0434\u0430\u043d\u0438\u044f.\n5. \u041f\u0440\u043e\u0434\u0430\u0432\u0435\u0446 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u043b \u0441\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u044c\u0441\u044f \u0434\u043b\u044f \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u044f \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u043f\u0440\u043e\u0435\u043a\u0442\u0430.\n6. \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0448\u0430\u0433 \u2014 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u043d\u044b\u0439 \u0437\u0432\u043e\u043d\u043e\u043a \u0434\u043b\u044f \u0431\u043e\u043b\u0435\u0435 \u0434\u0435\u0442\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u044f.", "budget_mentioned": true}','[{"date": "2025-08-27T12:50:03.468192", "channel": "avito", "summary": "1. \u041a\u043b\u0438\u0435\u043d\u0442 \u0441\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u043b \u043e \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0438 \u0442\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c \u0431\u043e\u0442\u0430 \u0434\u043b\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0434\u0430\u0436\u0438 \u0443\u0433\u043b\u044f.\n2. \u0418\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442 \u0443\u0441\u043b\u0443\u0433\u0430 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0442\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c \u0431\u043e\u0442\u0430 \u0438\u043b\u0438 \u043c\u0438\u043d\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f.\n3. \u0411\u044e\u0434\u0436\u0435\u0442 \u043d\u0435 \u0443\u043f\u043e\u043c\u0438\u043d\u0430\u043b\u0441\u044f.\n4. \u041a\u043b\u0438\u0435\u043d\u0442 \u0433\u043e\u0442\u043e\u0432 \u043a \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u0447\u0435\u0441\u0442\u0432\u0443 \u0438 \u0441\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043e \u043f\u043e\u043c\u043e\u0449\u0438 \u0432 \u0441\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u0438\u0438 \u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0437\u0430\u0434\u0430\u043d\u0438\u044f.\n5. \u041f\u0440\u043e\u0434\u0430\u0432\u0435\u0446 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u043b \u0441\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u044c\u0441\u044f \u0434\u043b\u044f \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u044f \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u043f\u0440\u043e\u0435\u043a\u0442\u0430.\n6. \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0448\u0430\u0433 \u2014 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u043d\u044b\u0439 \u0437\u0432\u043e\u043d\u043e\u043a \u0434\u043b\u044f \u0431\u043e\u043b\u0435\u0435 \u0434\u0435\u0442\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u043e\u0431\u0441\u0443\u0436\u0434\u0435\u043d\u0438\u044f.", "chat_id": "u2i-Hv_Ky68MuN8PtQNpsiDLdQ"}]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-08-27 09:50:03.475815','2025-08-27 09:50:03.475819',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(3,'амыавмава','INDIVIDUAL','NEW','','','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null','site','Клиент создан из лида: вамвамсфам',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-08-27 09:52:42.417119','2025-08-27 09:52:42.417123',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(4,'Клиент 50','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,50,'2025-10-18 08:03:47.353247','2025-10-18 08:03:47.353251',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(5,'уцвуцву','INDIVIDUAL','NEW',NULL,'цувув',NULL,NULL,NULL,'цвуцувцвв',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:28:53.548389','2025-10-18 14:28:53.548393',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(6,'уцвуцву','INDIVIDUAL','NEW',NULL,'цувув',NULL,NULL,NULL,'цвуцувцвв',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:28:55.648416','2025-10-18 14:28:55.648420',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(7,'уцвуцву','INDIVIDUAL','NEW',NULL,'цувув',NULL,NULL,NULL,'цвуцувцвв',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:28:55.729693','2025-10-18 14:28:55.729697',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(8,'уцвуцву','INDIVIDUAL','NEW',NULL,'цувув',NULL,NULL,NULL,'цвуцувцвв',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:28:55.878045','2025-10-18 14:28:55.878049',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(9,'ло','INDIVIDUAL','NEW','лололжо','длтдл',NULL,'длтдл',NULL,'длтдло',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:32:56.016556','2025-10-18 14:32:56.016560',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(10,'ло','INDIVIDUAL','NEW','лололжо','длтдл',NULL,'длтдл',NULL,'длтдло',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:32:57.455312','2025-10-18 14:32:57.455317',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(11,'ло','INDIVIDUAL','NEW','лололжо','длтдл',NULL,'длтдл',NULL,'длтдло',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:32:58.228385','2025-10-18 14:32:58.228388',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(12,'ло','INDIVIDUAL','NEW','лололжо','длтдл',NULL,'длтдл',NULL,'длтдло',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:32:58.394342','2025-10-18 14:32:58.394346',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(13,'уувувуцв','INDIVIDUAL','NEW','вуцвцув','увуцвувц',NULL,'увцувцув',NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:33:08.455459','2025-10-18 14:33:08.455462',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(14,'увувувв','INDIVIDUAL','NEW','вуувву','вуувув',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:34:20.595094','2025-10-18 14:34:20.595099',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(15,'увувцв','INDIVIDUAL','NEW','вууцв','вууцв',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:38.595316','2025-10-18 14:37:38.595319',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(16,'увувцв','INDIVIDUAL','NEW','вууцв','вууцв',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:42.704743','2025-10-18 14:37:42.704746',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(17,'увцувуц','INDIVIDUAL','NEW',NULL,'вуув',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:52.674104','2025-10-18 14:37:52.674108',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(18,'увцувуц','INDIVIDUAL','NEW',NULL,'вуув',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:53.012787','2025-10-18 14:37:53.012790',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(19,'увцувуц','INDIVIDUAL','NEW',NULL,'вуув',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:53.152733','2025-10-18 14:37:53.152737',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(20,'увцувуц','INDIVIDUAL','NEW',NULL,'вуув',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-18 14:37:53.323689','2025-10-18 14:37:53.323692',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(21,'Regina','INDIVIDUAL','NEW',NULL,NULL,'@reg_queen',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,51,'2025-10-20 11:47:07.240156','2025-10-20 11:47:07.240161',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(22,'Егор','INDIVIDUAL','NEW',NULL,NULL,'@vbpsdkr',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,52,'2025-10-20 11:47:23.468968','2025-10-20 11:47:23.468972',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(23,'F.O','INDIVIDUAL','NEW',NULL,NULL,'@fo_support',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,53,'2025-10-20 14:44:49.248523','2025-10-20 14:44:49.248529',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(24,'Oleg','INDIVIDUAL','NEW',NULL,NULL,'@zv3zdochka',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,54,'2025-10-21 11:36:12.052966','2025-10-21 11:36:12.052971',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(25,'Denis K','INDIVIDUAL','NEW','+79160074049',NULL,'@denis_k_1761304232',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,55,'2025-10-24 11:10:32.116052','2025-10-24 11:10:32.116057',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(26,'Николай Бот доступ к группам','INDIVIDUAL','NEW','+7 926 436 7178',NULL,'@николай_бот_доступ_к_группам_1761306666',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,56,'2025-10-24 11:51:06.984496','2025-10-24 11:51:06.984501',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(27,'Sdroal','INDIVIDUAL','NEW',NULL,NULL,'@Sdroal',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,57,'2025-10-24 11:54:58.984933','2025-10-24 11:54:58.984938',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(28,'Alexandr','INDIVIDUAL','NEW',NULL,NULL,'@Aleksandr_Alekseevlch',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,58,'2025-10-24 12:11:56.761528','2025-10-24 12:11:56.761532',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(29,'01992292','INDIVIDUAL','NEW',NULL,NULL,'@q0e6q',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,59,'2025-10-24 15:26:37.057630','2025-10-24 15:26:37.057635',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(30,'Denis','INDIVIDUAL','NEW',NULL,NULL,'@DKvip11',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,60,'2025-10-24 18:30:36.292152','2025-10-24 18:30:36.292157',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(31,'Тестовый клиент','INDIVIDUAL','NEW','+79001234567','test@example.com',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-26 11:58:02.692490','2025-10-26 11:58:02.692494',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(32,'fwfwef','INDIVIDUAL','NEW','effeef',NULL,NULL,NULL,NULL,'ffwf',NULL,NULL,NULL,NULL,'null',NULL,NULL,NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,NULL,'2025-10-26 12:02:45.098268','2025-10-26 12:02:45.098272',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(33,'Lay Traces','INDIVIDUAL','NEW',NULL,NULL,'@laytraces',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel_project','Создан автоматически при создании проекта',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,1,'2025-11-01 11:03:22.688634','2025-11-01 11:03:22.688638',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(34,'Клиент','INDIVIDUAL','NEW',NULL,NULL,'@client_1762008199',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,61,'2025-11-01 14:43:20.013806','2025-11-01 14:43:20.013811',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(35,'Клиент','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel','Создан автоматически при создании проекта ''ааккуа''',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,NULL,61,'2025-11-01 14:43:20.024199','2025-11-01 14:43:20.024202',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(36,'Клиент','INDIVIDUAL','NEW',NULL,NULL,'@client_1762008211',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,62,'2025-11-01 14:43:31.652185','2025-11-01 14:43:31.652190',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(37,'Клиент','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel','Создан автоматически при создании проекта ''ааккуа''',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,NULL,62,'2025-11-01 14:43:31.653646','2025-11-01 14:43:31.653648',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(38,'Клиент','INDIVIDUAL','NEW',NULL,NULL,'@client_1762008230',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,63,'2025-11-01 14:43:50.754708','2025-11-01 14:43:50.754711',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(39,'Клиент','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel','Создан автоматически при создании проекта ''ааккуа''',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,NULL,63,'2025-11-01 14:43:50.764468','2025-11-01 14:43:50.764470',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(40,'щшкра','INDIVIDUAL','NEW',NULL,NULL,'@щшкра_1762008620',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,64,'2025-11-01 14:50:20.941853','2025-11-01 14:50:20.941858',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(41,'щшкра','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel','Создан автоматически при создании проекта ''привте''',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,NULL,64,'2025-11-01 14:50:20.949515','2025-11-01 14:50:20.949518',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(42,'кхащштукхащшу','INDIVIDUAL','NEW','уахщшкашщ',NULL,'@кхащштукхащшу_1762009934',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,65,'2025-11-01 15:12:14.587358','2025-11-01 15:12:14.587363',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(43,'кхащштукхащшу','INDIVIDUAL','NEW','уахщшкашщ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'admin_panel','Создан автоматически при создании проекта ''зшпоаукшзгаухшка''',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,NULL,65,'2025-11-01 15:12:14.589403','2025-11-01 15:12:14.589405',1,NULL,NULL,NULL,'[]',NULL,NULL);
INSERT INTO clients VALUES(44,'Клиент 67','INDIVIDUAL','NEW',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'auto_user_creation','Создан автоматически при регистрации пользователя',NULL,'[]',0.0,0.0,NULL,NULL,0,NULL,NULL,1,67,'2025-11-06 15:07:46.237003','2025-11-06 15:07:46.237008',1,NULL,NULL,NULL,'[]',NULL,NULL);
CREATE TABLE leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        status VARCHAR(30) DEFAULT 'new',
        source VARCHAR(100),
        client_id INTEGER,
        contact_name VARCHAR(300),
        contact_phone VARCHAR(50),
        contact_email VARCHAR(255),
        contact_telegram VARCHAR(100),
        description TEXT,
        requirements TEXT,
        budget REAL,
        probability INTEGER DEFAULT 50,
        expected_close_date DATETIME,
        next_action_date DATETIME,
        interactions JSON DEFAULT '[]',
        notes TEXT,
        lost_reason VARCHAR(500),
        manager_id INTEGER,
        converted_to_deal_id INTEGER,
        converted_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER, utm_source VARCHAR(255), utm_medium VARCHAR(255), utm_campaign VARCHAR(255), assigned_to INTEGER, last_contact_date DATETIME, conversion_date DATETIME, rejection_reason TEXT, priority VARCHAR(20) DEFAULT 'normal', tags JSON, source_type TEXT, company_name TEXT, company_sphere TEXT, company_website TEXT, company_address TEXT, company_size TEXT, contact_whatsapp TEXT, call_history TEXT, email_history TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (converted_to_deal_id) REFERENCES deals(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    );
INSERT INTO leads VALUES(1,'вамвамсфам','NEW','site',NULL,'амыавмава','','','','мымавмвымамы',NULL,NULL,50,NULL,NULL,'[{"date": "2025-08-27T09:51:57.627653", "type": "status_change", "old_status": "new", "new_status": "contact_made", "user_id": 1, "user_name": "admin"}]',NULL,NULL,1,NULL,NULL,'2025-08-27 09:51:51.522011','2025-08-28 04:46:35.997968',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'','[]','[]');
INSERT INTO leads VALUES(2,'Лид Avito','NEW','avito_chat_u2i-mz5UTL5Wg4cH2N2dwrqqLw',NULL,'Лид Avito','','','','разработка приложения для изучения слов в формате флеш-карточек по типу Quizlet',NULL,NULL,50,NULL,NULL,'[]',replace('Создан из Avito чата u2i-mz5UTL5Wg4cH2N2dwrqqLw. Требования: разработка приложения для изучения слов в формате флеш-карточек по типу Quizlet\n\nИстория диалога:\nАвтор: Давайте свяжемся в телеграме , отправлю вам примеры\nАвтор: Сделаем\nАвтор: Здравствуйте\nАвтор: Мне нужно разработать приложение для изучения слов в формате флеш-карточек по типу Quizlet\nАвтор: Здравствуйте','\n',char(10)),NULL,NULL,NULL,NULL,'2025-08-28 05:42:46.638784','2025-08-28 05:42:46.638787',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'[]','[]');
INSERT INTO leads VALUES(3,'"ВАЛАНТИС" Ювелирный трейд-ин','NEW','avito',NULL,'','','','','Набрать',NULL,NULL,50,NULL,NULL,'[]',NULL,NULL,1,NULL,NULL,'2025-08-29 13:20:11.671096','2025-08-29 13:20:11.671100',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'89689009080','[]','[]');
INSERT INTO leads VALUES(4,'"Jewelry Outlet Kehle" ювелирные изделия','NEW','avito',NULL,'Николай','89137832008','','','Запасной номер коммерческого директора девушки 89267334211',NULL,NULL,50,NULL,NULL,'[]',NULL,NULL,1,NULL,NULL,'2025-08-29 13:43:46.761016','2025-08-29 13:43:46.761020',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'89137832008 ','[]','[]');
INSERT INTO leads VALUES(5,'RUSSIAN JEWELER - ЮВЕЛИРНОЕ АТЕЛЬЕ № 1','NEW','site',NULL,'Гармония (в тг Ване писал)','','','@Garmoniya777','',NULL,NULL,50,NULL,NULL,'[]',NULL,NULL,1,NULL,NULL,'2025-08-29 13:48:16.597943','2025-08-29 13:48:16.597946',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'','[]','[]');
INSERT INTO leads VALUES(6,'"Золото и бриллианты" Ювелирные изделия','NEW','avito',NULL,'Марина','88161554453','','','Отправить демку ',NULL,NULL,50,NULL,NULL,'[]',NULL,NULL,1,NULL,NULL,'2025-08-29 16:04:39.513818','2025-08-29 16:04:39.513825',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'88161554453','[]','[]');
INSERT INTO leads VALUES(7,'Ольга ( авитовелирка)','CONTACT_MADE','avito',NULL,'Ольга','-','','','',NULL,NULL,50,NULL,NULL,'[{"date": "2025-09-03T11:17:08.161049", "type": "status_change", "old_status": "new", "new_status": "contact_made", "user_id": 1, "user_name": "admin"}]',NULL,NULL,1,NULL,NULL,'2025-09-03 11:17:01.541886','2025-09-03 11:17:08.161037',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'normal','[]',NULL,NULL,NULL,NULL,NULL,NULL,'','[]','[]');
CREATE TABLE deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        status VARCHAR(30) DEFAULT 'new',
        client_id INTEGER NOT NULL,
        description TEXT,
        technical_requirements JSON,
        amount REAL NOT NULL,
        cost REAL,
        margin REAL,
        discount REAL DEFAULT 0.0,
        prepayment_percent INTEGER DEFAULT 50,
        prepayment_amount REAL DEFAULT 0.0,
        paid_amount REAL DEFAULT 0.0,
        payment_schedule JSON,
        start_date DATETIME,
        end_date DATETIME,
        actual_start_date DATETIME,
        actual_end_date DATETIME,
        contract_number VARCHAR(100),
        contract_date DATETIME,
        contract_signed BOOLEAN DEFAULT 0,
        act_number VARCHAR(100),
        act_date DATETIME,
        project_id INTEGER,
        manager_id INTEGER,
        executor_id INTEGER,
        priority VARCHAR(20) DEFAULT 'normal',
        tags JSON DEFAULT '[]',
        custom_fields JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        closed_at DATETIME,
        created_by_id INTEGER, converted_to_project_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (manager_id) REFERENCES admin_users(id),
        FOREIGN KEY (executor_id) REFERENCES admin_users(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    );
CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type VARCHAR(50) NOT NULL,
        name VARCHAR(500) NOT NULL,
        number VARCHAR(100),
        client_id INTEGER,
        deal_id INTEGER,
        project_id INTEGER,
        file_path VARCHAR(500),
        file_size INTEGER,
        file_type VARCHAR(50),
        template_id INTEGER,
        content JSON,
        generated_html TEXT,
        status VARCHAR(50) DEFAULT 'draft',
        date DATETIME,
        valid_until DATETIME,
        signed_at DATETIME,
        description TEXT,
        tags JSON DEFAULT '[]',
        metadata JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (deal_id) REFERENCES deals(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (template_id) REFERENCES document_templates(id),
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    );
CREATE TABLE document_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        type VARCHAR(50) NOT NULL,
        description TEXT,
        template_html TEXT NOT NULL,
        variables JSON NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_default BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        FOREIGN KEY (created_by_id) REFERENCES admin_users(id)
    );
CREATE TABLE client_tag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        color VARCHAR(20),
        description TEXT
    );
CREATE TABLE client_tags (
        client_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (client_id, tag_id),
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (tag_id) REFERENCES client_tag(id)
    );
CREATE TABLE service_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(300) NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT,
        base_price REAL NOT NULL,
        min_price REAL,
        max_price REAL,
        estimated_hours INTEGER,
        estimated_days INTEGER,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        tags JSON DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE deal_services (
        deal_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        PRIMARY KEY (deal_id, service_id),
        FOREIGN KEY (deal_id) REFERENCES deals(id),
        FOREIGN KEY (service_id) REFERENCES service_catalog(id)
    );
CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action VARCHAR(100) NOT NULL,
        entity_type VARCHAR(50) NOT NULL,
        entity_id INTEGER,
        old_data JSON,
        new_data JSON,
        changes JSON,
        description TEXT,
        ip_address VARCHAR(50),
        user_agent VARCHAR(500),
        request_id VARCHAR(100),
        user_id INTEGER,
        user_name VARCHAR(200),
        user_role VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES admin_users(id)
    );
CREATE TABLE roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        display_name VARCHAR(200) NOT NULL,
        description TEXT,
        level INTEGER DEFAULT 0,
        is_system BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        max_projects INTEGER,
        max_clients INTEGER,
        max_deals INTEGER,
        modules_access JSON DEFAULT '{}',
        dashboard_widgets JSON DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO roles VALUES(1,'owner','Владелец','Полный доступ ко всем функциям системы',100,1,1,NULL,NULL,NULL,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
INSERT INTO roles VALUES(2,'admin','Администратор','Административный доступ с ограничениями',90,1,1,NULL,NULL,NULL,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
INSERT INTO roles VALUES(3,'manager','Менеджер','Управление клиентами и сделками',50,1,1,NULL,100,50,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
INSERT INTO roles VALUES(4,'executor','Исполнитель','Работа с назначенными проектами',30,1,1,20,NULL,NULL,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
INSERT INTO roles VALUES(5,'accountant','Бухгалтер','Доступ к финансовым данным',40,1,1,NULL,NULL,NULL,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
INSERT INTO roles VALUES(6,'observer','Наблюдатель','Только просмотр данных',10,1,1,NULL,NULL,NULL,'{}','[]','2025-08-17 08:25:39','2025-08-17 08:25:39');
CREATE TABLE permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        display_name VARCHAR(200) NOT NULL,
        description TEXT,
        module VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        conditions JSON,
        is_system BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO permissions VALUES(1,'projects.view','Просмотр проектов','Просмотр списка и деталей проектов','projects','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(2,'projects.create','Создание проектов','Создание новых проектов','projects','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(3,'projects.edit','Редактирование проектов','Изменение данных проектов','projects','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(4,'projects.delete','Удаление проектов','Удаление проектов','projects','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(5,'projects.export','Экспорт проектов','Экспорт данных проектов','projects','export',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(6,'clients.view','Просмотр клиентов','Просмотр списка и деталей клиентов','clients','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(7,'clients.create','Создание клиентов','Создание новых клиентов','clients','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(8,'clients.edit','Редактирование клиентов','Изменение данных клиентов','clients','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(9,'clients.delete','Удаление клиентов','Удаление клиентов','clients','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(10,'clients.export','Экспорт клиентов','Экспорт данных клиентов','clients','export',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(11,'leads.view','Просмотр лидов','Просмотр списка и деталей лидов','leads','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(12,'leads.create','Создание лидов','Создание новых лидов','leads','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(13,'leads.edit','Редактирование лидов','Изменение данных лидов','leads','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(14,'leads.delete','Удаление лидов','Удаление лидов','leads','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(15,'leads.convert','Конвертация лидов','Конвертация лидов в сделки','leads','convert',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(16,'deals.view','Просмотр сделок','Просмотр списка и деталей сделок','deals','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(17,'deals.create','Создание сделок','Создание новых сделок','deals','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(18,'deals.edit','Редактирование сделок','Изменение данных сделок','deals','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(19,'deals.delete','Удаление сделок','Удаление сделок','deals','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(20,'deals.export','Экспорт сделок','Экспорт данных сделок','deals','export',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(21,'finance.view','Просмотр финансов','Просмотр финансовых данных','finance','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(22,'finance.create','Создание транзакций','Создание финансовых транзакций','finance','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(23,'finance.edit','Редактирование финансов','Изменение финансовых данных','finance','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(24,'finance.delete','Удаление транзакций','Удаление финансовых транзакций','finance','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(25,'finance.export','Экспорт финансов','Экспорт финансовых отчетов','finance','export',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(26,'documents.view','Просмотр документов','Просмотр документов','documents','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(27,'documents.create','Создание документов','Создание новых документов','documents','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(28,'documents.edit','Редактирование документов','Изменение документов','documents','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(29,'documents.delete','Удаление документов','Удаление документов','documents','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(30,'documents.sign','Подписание документов','Право подписи документов','documents','sign',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(31,'reports.view','Просмотр отчетов','Просмотр отчетов и аналитики','reports','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(32,'reports.export','Экспорт отчетов','Экспорт отчетов','reports','export',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(33,'settings.view','Просмотр настроек','Просмотр настроек системы','settings','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(34,'settings.edit','Изменение настроек','Изменение настроек системы','settings','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(35,'users.view','Просмотр пользователей','Просмотр списка пользователей','users','view',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(36,'users.create','Создание пользователей','Создание новых пользователей','users','create',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(37,'users.edit','Редактирование пользователей','Изменение данных пользователей','users','edit',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(38,'users.delete','Удаление пользователей','Удаление пользователей','users','delete',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(39,'users.roles','Управление ролями','Назначение ролей пользователям','users','roles',NULL,1,'2025-08-17 08:25:39');
INSERT INTO permissions VALUES(40,'dashboard.view','Дашборд - view','Разрешение view для модуля dashboard','dashboard','view',NULL,0,'2025-11-05 08:17:05.125563');
INSERT INTO permissions VALUES(41,'leads.export','Лиды - export','Разрешение export для модуля leads','leads','export',NULL,0,'2025-11-05 08:17:05.150260');
INSERT INTO permissions VALUES(42,'clients.contact','Клиенты - contact','Разрешение contact для модуля clients','clients','contact',NULL,0,'2025-11-05 08:17:05.171575');
INSERT INTO permissions VALUES(43,'deals.close','Сделки - close','Разрешение close для модуля deals','deals','close',NULL,0,'2025-11-05 08:17:05.189060');
INSERT INTO permissions VALUES(44,'avito.view','Avito интеграция - view','Разрешение view для модуля avito','avito','view',NULL,0,'2025-11-05 08:17:05.196633');
INSERT INTO permissions VALUES(45,'avito.messages.send','Avito интеграция - messages.send','Разрешение messages.send для модуля avito','avito','messages.send',NULL,0,'2025-11-05 08:17:05.203492');
CREATE TABLE role_permissions (
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (role_id, permission_id),
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (permission_id) REFERENCES permissions(id)
    );
INSERT INTO role_permissions VALUES(1,6);
INSERT INTO role_permissions VALUES(1,7);
INSERT INTO role_permissions VALUES(1,8);
INSERT INTO role_permissions VALUES(1,9);
INSERT INTO role_permissions VALUES(1,10);
INSERT INTO role_permissions VALUES(1,16);
INSERT INTO role_permissions VALUES(1,17);
INSERT INTO role_permissions VALUES(1,18);
INSERT INTO role_permissions VALUES(1,19);
INSERT INTO role_permissions VALUES(1,20);
INSERT INTO role_permissions VALUES(1,26);
INSERT INTO role_permissions VALUES(1,27);
INSERT INTO role_permissions VALUES(1,28);
INSERT INTO role_permissions VALUES(1,29);
INSERT INTO role_permissions VALUES(1,30);
INSERT INTO role_permissions VALUES(1,21);
INSERT INTO role_permissions VALUES(1,22);
INSERT INTO role_permissions VALUES(1,23);
INSERT INTO role_permissions VALUES(1,24);
INSERT INTO role_permissions VALUES(1,25);
INSERT INTO role_permissions VALUES(1,11);
INSERT INTO role_permissions VALUES(1,12);
INSERT INTO role_permissions VALUES(1,13);
INSERT INTO role_permissions VALUES(1,14);
INSERT INTO role_permissions VALUES(1,15);
INSERT INTO role_permissions VALUES(1,1);
INSERT INTO role_permissions VALUES(1,2);
INSERT INTO role_permissions VALUES(1,3);
INSERT INTO role_permissions VALUES(1,4);
INSERT INTO role_permissions VALUES(1,5);
INSERT INTO role_permissions VALUES(1,31);
INSERT INTO role_permissions VALUES(1,32);
INSERT INTO role_permissions VALUES(1,33);
INSERT INTO role_permissions VALUES(1,34);
INSERT INTO role_permissions VALUES(1,35);
INSERT INTO role_permissions VALUES(1,36);
INSERT INTO role_permissions VALUES(1,37);
INSERT INTO role_permissions VALUES(1,38);
INSERT INTO role_permissions VALUES(1,39);
CREATE TABLE user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (role_id) REFERENCES roles(id)
    );
INSERT INTO user_roles VALUES(1,1);
INSERT INTO user_roles VALUES(3,4);
INSERT INTO user_roles VALUES(4,4);
INSERT INTO user_roles VALUES(5,4);
INSERT INTO user_roles VALUES(7,4);
INSERT INTO user_roles VALUES(8,4);
INSERT INTO user_roles VALUES(9,4);
CREATE TABLE user_permissions (
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, permission_id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (permission_id) REFERENCES permissions(id)
    );
INSERT INTO user_permissions VALUES(12,40);
INSERT INTO user_permissions VALUES(12,11);
INSERT INTO user_permissions VALUES(12,12);
INSERT INTO user_permissions VALUES(12,13);
INSERT INTO user_permissions VALUES(12,41);
INSERT INTO user_permissions VALUES(12,15);
INSERT INTO user_permissions VALUES(12,6);
INSERT INTO user_permissions VALUES(12,7);
INSERT INTO user_permissions VALUES(12,8);
INSERT INTO user_permissions VALUES(12,10);
INSERT INTO user_permissions VALUES(12,42);
INSERT INTO user_permissions VALUES(12,16);
INSERT INTO user_permissions VALUES(12,17);
INSERT INTO user_permissions VALUES(12,18);
INSERT INTO user_permissions VALUES(12,20);
INSERT INTO user_permissions VALUES(12,43);
INSERT INTO user_permissions VALUES(12,44);
INSERT INTO user_permissions VALUES(12,45);
CREATE TABLE data_access_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER,
        user_id INTEGER,
        entity_type VARCHAR(50) NOT NULL,
        access_type VARCHAR(20) NOT NULL,
        conditions JSON,
        specific_ids JSON,
        can_view BOOLEAN DEFAULT 1,
        can_edit BOOLEAN DEFAULT 0,
        can_delete BOOLEAN DEFAULT 0,
        can_export BOOLEAN DEFAULT 0,
        priority INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (user_id) REFERENCES admin_users(id)
    );
INSERT INTO data_access_rules VALUES(1,NULL,12,'dashboard','own',NULL,NULL,1,0,0,1,10,1,'2025-11-05 08:17:05.149431','2025-11-05 08:17:05.149437');
INSERT INTO data_access_rules VALUES(2,NULL,12,'leads','own',NULL,NULL,1,1,0,1,10,1,'2025-11-05 08:17:05.171030','2025-11-05 08:17:05.171034');
INSERT INTO data_access_rules VALUES(3,NULL,12,'clients','own',NULL,NULL,1,1,0,1,10,1,'2025-11-05 08:17:05.188535','2025-11-05 08:17:05.188540');
INSERT INTO data_access_rules VALUES(4,NULL,12,'deals','own',NULL,NULL,1,1,0,1,10,1,'2025-11-05 08:17:05.196017','2025-11-05 08:17:05.196023');
INSERT INTO data_access_rules VALUES(5,NULL,12,'avito','own',NULL,NULL,1,1,0,0,10,1,'2025-11-05 08:17:05.205079','2025-11-05 08:17:05.205083');
CREATE TABLE teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        leader_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (leader_id) REFERENCES admin_users(id)
    );
CREATE TABLE team_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        team_role VARCHAR(50) DEFAULT 'member',
        can_see_team_data BOOLEAN DEFAULT 1,
        can_edit_team_data BOOLEAN DEFAULT 0,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES admin_users(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    );
CREATE TABLE audit_log (
	id INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	action_type VARCHAR(18) NOT NULL, 
	user_id INTEGER, 
	user_email VARCHAR(200), 
	user_role VARCHAR(100), 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	session_id VARCHAR(100), 
	entity_type VARCHAR(10), 
	entity_id INTEGER, 
	entity_name VARCHAR(500), 
	description TEXT, 
	old_values JSON, 
	new_values JSON, 
	changed_fields JSON, 
	extra_metadata JSON, 
	success VARCHAR(10), 
	error_message TEXT, 
	duration_ms INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES admin_users (id)
);
INSERT INTO audit_log VALUES(1,'2025-08-27 09:51:51.534009','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Создан лид: вамвамсфам',NULL,'{"id": 1, "title": "\u0432\u0430\u043c\u0432\u0430\u043c\u0441\u0444\u0430\u043c", "status": "new", "source": "site", "client_id": null, "contact_name": "\u0430\u043c\u044b\u0430\u0432\u043c\u0430\u0432\u0430", "contact_phone": "", "contact_email": "", "contact_telegram": "", "contact_whatsapp": "", "description": "\u043c\u044b\u043c\u0430\u0432\u043c\u0432\u044b\u043c\u0430\u043c\u044b", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-08-27T09:51:51.522011", "updated_at": "2025-08-27T09:51:51.522019", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(2,'2025-08-27 09:51:57.635627','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': new → contact_made','{"status": "new"}','{"status": "contact_made"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(3,'2025-08-27 09:52:30.596030','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': contact_made → new','{"status": "contact_made"}','{"status": "new"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(4,'2025-08-27 09:55:10.711054','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': new → contact_made','{"status": "new"}','{"status": "contact_made"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(5,'2025-08-27 09:55:12.105340','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': contact_made → new','{"status": "contact_made"}','{"status": "new"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(6,'2025-08-28 04:46:34.692498','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': new → contact_made','{"status": "new"}','{"status": "contact_made"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(7,'2025-08-28 04:46:36.002829','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',1,NULL,'Изменен статус лида ''вамвамсфам'': contact_made → new','{"status": "contact_made"}','{"status": "new"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(8,'2025-08-29 13:20:11.681891','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',3,NULL,'Создан лид: "ВАЛАНТИС" Ювелирный трейд-ин',NULL,'{"id": 3, "title": "\"\u0412\u0410\u041b\u0410\u041d\u0422\u0418\u0421\" \u042e\u0432\u0435\u043b\u0438\u0440\u043d\u044b\u0439 \u0442\u0440\u0435\u0439\u0434-\u0438\u043d", "status": "new", "source": "avito", "client_id": null, "contact_name": "", "contact_phone": "", "contact_email": "", "contact_telegram": "", "contact_whatsapp": "89689009080", "description": "\u041d\u0430\u0431\u0440\u0430\u0442\u044c", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-08-29T13:20:11.671096", "updated_at": "2025-08-29T13:20:11.671100", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(9,'2025-08-29 13:43:46.766753','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',4,NULL,'Создан лид: "Jewelry Outlet Kehle" ювелирные изделия',NULL,'{"id": 4, "title": "\"Jewelry Outlet Kehle\" \u044e\u0432\u0435\u043b\u0438\u0440\u043d\u044b\u0435 \u0438\u0437\u0434\u0435\u043b\u0438\u044f", "status": "new", "source": "avito", "client_id": null, "contact_name": "\u041d\u0438\u043a\u043e\u043b\u0430\u0439", "contact_phone": "89137832008", "contact_email": "", "contact_telegram": "", "contact_whatsapp": "89137832008 ", "description": "\u0417\u0430\u043f\u0430\u0441\u043d\u043e\u0439 \u043d\u043e\u043c\u0435\u0440 \u043a\u043e\u043c\u043c\u0435\u0440\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440\u0430 \u0434\u0435\u0432\u0443\u0448\u043a\u0438 89267334211", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-08-29T13:43:46.761016", "updated_at": "2025-08-29T13:43:46.761020", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(10,'2025-08-29 13:48:16.619085','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',5,NULL,'Создан лид: RUSSIAN JEWELER - ЮВЕЛИРНОЕ АТЕЛЬЕ № 1',NULL,'{"id": 5, "title": "RUSSIAN JEWELER - \u042e\u0412\u0415\u041b\u0418\u0420\u041d\u041e\u0415 \u0410\u0422\u0415\u041b\u042c\u0415 \u2116 1", "status": "new", "source": "site", "client_id": null, "contact_name": "\u0413\u0430\u0440\u043c\u043e\u043d\u0438\u044f (\u0432 \u0442\u0433 \u0412\u0430\u043d\u0435 \u043f\u0438\u0441\u0430\u043b)", "contact_phone": "", "contact_email": "", "contact_telegram": "@Garmoniya777", "contact_whatsapp": "", "description": "", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-08-29T13:48:16.597943", "updated_at": "2025-08-29T13:48:16.597946", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(11,'2025-08-29 16:04:39.519785','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',6,NULL,'Создан лид: "Золото и бриллианты" Ювелирные изделия',NULL,'{"id": 6, "title": "\"\u0417\u043e\u043b\u043e\u0442\u043e \u0438 \u0431\u0440\u0438\u043b\u043b\u0438\u0430\u043d\u0442\u044b\" \u042e\u0432\u0435\u043b\u0438\u0440\u043d\u044b\u0435 \u0438\u0437\u0434\u0435\u043b\u0438\u044f", "status": "new", "source": "avito", "client_id": null, "contact_name": "\u041c\u0430\u0440\u0438\u043d\u0430", "contact_phone": "88161554453", "contact_email": "", "contact_telegram": "", "contact_whatsapp": "88161554453", "description": "\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0434\u0435\u043c\u043a\u0443 ", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-08-29T16:04:39.513818", "updated_at": "2025-08-29T16:04:39.513825", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(12,'2025-09-03 11:17:01.557349','CREATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',7,NULL,'Создан лид: Ольга ( авитовелирка)',NULL,'{"id": 7, "title": "\u041e\u043b\u044c\u0433\u0430 ( \u0430\u0432\u0438\u0442\u043e\u0432\u0435\u043b\u0438\u0440\u043a\u0430)", "status": "new", "source": "avito", "client_id": null, "contact_name": "\u041e\u043b\u044c\u0433\u0430", "contact_phone": "-", "contact_email": "", "contact_telegram": "", "contact_whatsapp": "", "description": "", "requirements": null, "budget": null, "probability": 50, "expected_close_date": null, "next_action_date": null, "interactions": [], "notes": null, "lost_reason": null, "manager_id": 1, "converted_to_deal_id": null, "converted_at": null, "created_at": "2025-09-03T11:17:01.541886", "updated_at": "2025-09-03T11:17:01.541895", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(13,'2025-09-03 11:17:08.168366','UPDATE',1,'admin',NULL,NULL,NULL,NULL,'LEAD',7,NULL,'Изменен статус лида ''Ольга ( авитовелирка)'': new → contact_made','{"status": "new"}','{"status": "contact_made"}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(14,'2025-10-18 14:28:53.568056','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',5,NULL,'Создан клиент: уцвуцву',NULL,'{"id": 5, "name": "\u0443\u0446\u0432\u0443\u0446\u0432\u0443", "type": "individual", "status": "new", "phone": null, "email": "\u0446\u0443\u0432\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": "\u0446\u0432\u0443\u0446\u0443\u0432\u0446\u0432\u0432", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:28:53.548389", "updated_at": "2025-10-18T14:28:53.548393", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(15,'2025-10-18 14:28:55.658296','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',6,NULL,'Создан клиент: уцвуцву',NULL,'{"id": 6, "name": "\u0443\u0446\u0432\u0443\u0446\u0432\u0443", "type": "individual", "status": "new", "phone": null, "email": "\u0446\u0443\u0432\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": "\u0446\u0432\u0443\u0446\u0443\u0432\u0446\u0432\u0432", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:28:55.648416", "updated_at": "2025-10-18T14:28:55.648420", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(16,'2025-10-18 14:28:55.746032','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',7,NULL,'Создан клиент: уцвуцву',NULL,'{"id": 7, "name": "\u0443\u0446\u0432\u0443\u0446\u0432\u0443", "type": "individual", "status": "new", "phone": null, "email": "\u0446\u0443\u0432\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": "\u0446\u0432\u0443\u0446\u0443\u0432\u0446\u0432\u0432", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:28:55.729693", "updated_at": "2025-10-18T14:28:55.729697", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(17,'2025-10-18 14:28:55.886108','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',8,NULL,'Создан клиент: уцвуцву',NULL,'{"id": 8, "name": "\u0443\u0446\u0432\u0443\u0446\u0432\u0443", "type": "individual", "status": "new", "phone": null, "email": "\u0446\u0443\u0432\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": "\u0446\u0432\u0443\u0446\u0443\u0432\u0446\u0432\u0432", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:28:55.878045", "updated_at": "2025-10-18T14:28:55.878049", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(18,'2025-10-18 14:32:56.029425','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',9,NULL,'Создан клиент: ло',NULL,'{"id": 9, "name": "\u043b\u043e", "type": "individual", "status": "new", "phone": "\u043b\u043e\u043b\u043e\u043b\u0436\u043e", "email": "\u0434\u043b\u0442\u0434\u043b", "telegram": null, "whatsapp": "\u0434\u043b\u0442\u0434\u043b", "website": null, "address": "\u0434\u043b\u0442\u0434\u043b\u043e", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:32:56.016556", "updated_at": "2025-10-18T14:32:56.016560", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(19,'2025-10-18 14:32:57.459393','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',10,NULL,'Создан клиент: ло',NULL,'{"id": 10, "name": "\u043b\u043e", "type": "individual", "status": "new", "phone": "\u043b\u043e\u043b\u043e\u043b\u0436\u043e", "email": "\u0434\u043b\u0442\u0434\u043b", "telegram": null, "whatsapp": "\u0434\u043b\u0442\u0434\u043b", "website": null, "address": "\u0434\u043b\u0442\u0434\u043b\u043e", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:32:57.455312", "updated_at": "2025-10-18T14:32:57.455317", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(20,'2025-10-18 14:32:58.237796','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',11,NULL,'Создан клиент: ло',NULL,'{"id": 11, "name": "\u043b\u043e", "type": "individual", "status": "new", "phone": "\u043b\u043e\u043b\u043e\u043b\u0436\u043e", "email": "\u0434\u043b\u0442\u0434\u043b", "telegram": null, "whatsapp": "\u0434\u043b\u0442\u0434\u043b", "website": null, "address": "\u0434\u043b\u0442\u0434\u043b\u043e", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:32:58.228385", "updated_at": "2025-10-18T14:32:58.228388", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(21,'2025-10-18 14:32:58.402174','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',12,NULL,'Создан клиент: ло',NULL,'{"id": 12, "name": "\u043b\u043e", "type": "individual", "status": "new", "phone": "\u043b\u043e\u043b\u043e\u043b\u0436\u043e", "email": "\u0434\u043b\u0442\u0434\u043b", "telegram": null, "whatsapp": "\u0434\u043b\u0442\u0434\u043b", "website": null, "address": "\u0434\u043b\u0442\u0434\u043b\u043e", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:32:58.394342", "updated_at": "2025-10-18T14:32:58.394346", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(22,'2025-10-18 14:33:08.459280','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',13,NULL,'Создан клиент: уувувуцв',NULL,'{"id": 13, "name": "\u0443\u0443\u0432\u0443\u0432\u0443\u0446\u0432", "type": "individual", "status": "new", "phone": "\u0432\u0443\u0446\u0432\u0446\u0443\u0432", "email": "\u0443\u0432\u0443\u0446\u0432\u0443\u0432\u0446", "telegram": null, "whatsapp": "\u0443\u0432\u0446\u0443\u0432\u0446\u0443\u0432", "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:33:08.455459", "updated_at": "2025-10-18T14:33:08.455462", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(23,'2025-10-18 14:34:20.604191','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',14,NULL,'Создан клиент: увувувв',NULL,'{"id": 14, "name": "\u0443\u0432\u0443\u0432\u0443\u0432\u0432", "type": "individual", "status": "new", "phone": "\u0432\u0443\u0443\u0432\u0432\u0443", "email": "\u0432\u0443\u0443\u0432\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:34:20.595094", "updated_at": "2025-10-18T14:34:20.595099", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(24,'2025-10-18 14:37:38.609237','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',15,NULL,'Создан клиент: увувцв',NULL,'{"id": 15, "name": "\u0443\u0432\u0443\u0432\u0446\u0432", "type": "individual", "status": "new", "phone": "\u0432\u0443\u0443\u0446\u0432", "email": "\u0432\u0443\u0443\u0446\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:38.595316", "updated_at": "2025-10-18T14:37:38.595319", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(25,'2025-10-18 14:37:42.714587','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',16,NULL,'Создан клиент: увувцв',NULL,'{"id": 16, "name": "\u0443\u0432\u0443\u0432\u0446\u0432", "type": "individual", "status": "new", "phone": "\u0432\u0443\u0443\u0446\u0432", "email": "\u0432\u0443\u0443\u0446\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:42.704743", "updated_at": "2025-10-18T14:37:42.704746", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(26,'2025-10-18 14:37:52.682304','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',17,NULL,'Создан клиент: увцувуц',NULL,'{"id": 17, "name": "\u0443\u0432\u0446\u0443\u0432\u0443\u0446", "type": "individual", "status": "new", "phone": null, "email": "\u0432\u0443\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:52.674104", "updated_at": "2025-10-18T14:37:52.674108", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(27,'2025-10-18 14:37:53.017076','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',18,NULL,'Создан клиент: увцувуц',NULL,'{"id": 18, "name": "\u0443\u0432\u0446\u0443\u0432\u0443\u0446", "type": "individual", "status": "new", "phone": null, "email": "\u0432\u0443\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:53.012787", "updated_at": "2025-10-18T14:37:53.012790", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(28,'2025-10-18 14:37:53.161929','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',19,NULL,'Создан клиент: увцувуц',NULL,'{"id": 19, "name": "\u0443\u0432\u0446\u0443\u0432\u0443\u0446", "type": "individual", "status": "new", "phone": null, "email": "\u0432\u0443\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:53.152733", "updated_at": "2025-10-18T14:37:53.152737", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(29,'2025-10-18 14:37:53.327319','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',20,NULL,'Создан клиент: увцувуц',NULL,'{"id": 20, "name": "\u0443\u0432\u0446\u0443\u0432\u0443\u0446", "type": "individual", "status": "new", "phone": null, "email": "\u0432\u0443\u0443\u0432", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-18T14:37:53.323689", "updated_at": "2025-10-18T14:37:53.323692", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(30,'2025-10-26 11:58:02.709634','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',31,NULL,'Создан клиент: Тестовый клиент',NULL,'{"id": 31, "name": "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439 \u043a\u043b\u0438\u0435\u043d\u0442", "type": "individual", "status": "new", "phone": "+79001234567", "email": "test@example.com", "telegram": null, "whatsapp": null, "website": null, "address": null, "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-26T11:58:02.692490", "updated_at": "2025-10-26T11:58:02.692494", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(31,'2025-10-26 12:02:45.108053','CREATE',1,NULL,NULL,NULL,NULL,NULL,'CLIENT',32,NULL,'Создан клиент: fwfwef',NULL,'{"id": 32, "name": "fwfwef", "type": "individual", "status": "new", "phone": "effeef", "email": null, "telegram": null, "whatsapp": null, "website": null, "address": "ffwf", "company_name": null, "inn": null, "kpp": null, "ogrn": null, "bank_details": null, "source": null, "description": null, "preferences": null, "total_revenue": 0.0, "average_check": 0.0, "payment_terms": null, "credit_limit": null, "rating": 0, "segment": null, "loyalty_level": null, "manager_id": 1, "telegram_user_id": null, "created_at": "2025-10-26T12:02:45.098268", "updated_at": "2025-10-26T12:02:45.098272", "created_by_id": 1}',NULL,NULL,'success',NULL,NULL);
INSERT INTO audit_log VALUES(32,'2025-11-05 08:17:05.223007','UPDATE',1,NULL,NULL,NULL,NULL,NULL,'USER',12,NULL,'Обновлены права доступа пользователя: omen',NULL,'{"dashboard": {"enabled": true, "permissions": {"view": true, "widgets.manage": false}, "data_access": {"type": "own", "can_view": true, "can_edit": false, "can_delete": false, "can_export": true}}, "leads": {"enabled": true, "permissions": {"view": true, "create": true, "edit": true, "delete": false, "export": true, "convert": true}, "data_access": {"type": "own", "can_view": true, "can_edit": true, "can_delete": false, "can_export": true}}, "clients": {"enabled": true, "permissions": {"view": true, "create": true, "edit": true, "delete": false, "export": true, "contact": true}, "data_access": {"type": "own", "can_view": true, "can_edit": true, "can_delete": false, "can_export": true}}, "deals": {"enabled": true, "permissions": {"view": true, "create": true, "edit": true, "delete": false, "export": true, "close": true}, "data_access": {"type": "own", "can_view": true, "can_edit": true, "can_delete": false, "can_export": true}}, "projects": {"enabled": true, "permissions": {"view": false, "create": false, "edit": false, "delete": false, "export": false, "assign": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}, "finance": {"enabled": true, "permissions": {"view": false, "create": false, "edit": false, "delete": false, "export": false, "reports": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}, "avito": {"enabled": true, "permissions": {"view": true, "messages.send": true, "chats.manage": false, "settings.edit": false}, "data_access": {"type": "own", "can_view": true, "can_edit": true, "can_delete": false, "can_export": false}}, "documents": {"enabled": true, "permissions": {"view": false, "create": false, "edit": false, "delete": false, "generate": false, "sign": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}, "reports": {"enabled": true, "permissions": {"view": false, "create": false, "export": false, "schedule": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}, "settings": {"enabled": true, "permissions": {"view": false, "edit": false, "system.manage": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}, "users": {"enabled": true, "permissions": {"view": false, "create": false, "edit": false, "delete": false, "permissions.manage": false}, "data_access": {"type": "none", "can_view": false, "can_edit": false, "can_delete": false, "can_export": false}}}',NULL,NULL,'success',NULL,NULL);
CREATE TABLE audit_sessions (
	id INTEGER NOT NULL, 
	session_id VARCHAR(100) NOT NULL, 
	user_id INTEGER NOT NULL, 
	started_at DATETIME NOT NULL, 
	ended_at DATETIME, 
	last_activity DATETIME, 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	browser VARCHAR(100), 
	os VARCHAR(100), 
	device_type VARCHAR(50), 
	country VARCHAR(100), 
	city VARCHAR(100), 
	actions_count INTEGER, 
	pages_visited JSON, 
	is_active VARCHAR(10), 
	termination_reason VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (session_id), 
	FOREIGN KEY(user_id) REFERENCES admin_users (id)
);
CREATE TABLE audit_data_changes (
	id INTEGER NOT NULL, 
	audit_log_id INTEGER NOT NULL, 
	field_name VARCHAR(100) NOT NULL, 
	field_type VARCHAR(50), 
	old_value TEXT, 
	new_value TEXT, 
	field_label VARCHAR(200), 
	is_sensitive VARCHAR(10), 
	PRIMARY KEY (id), 
	FOREIGN KEY(audit_log_id) REFERENCES audit_log (id)
);
CREATE TABLE audit_alerts (
	id INTEGER NOT NULL, 
	alert_type VARCHAR(100) NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	user_id INTEGER, 
	session_id VARCHAR(100), 
	ip_address VARCHAR(45), 
	details JSON, 
	created_at DATETIME NOT NULL, 
	is_resolved VARCHAR(10), 
	resolved_at DATETIME, 
	resolved_by INTEGER, 
	resolution_notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES admin_users (id), 
	FOREIGN KEY(resolved_by) REFERENCES admin_users (id)
);
CREATE TABLE audit_reports (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	report_type VARCHAR(100), 
	date_from DATETIME, 
	date_to DATETIME, 
	filters JSON, 
	data JSON, 
	summary JSON, 
	file_path VARCHAR(500), 
	file_format VARCHAR(20), 
	generated_at DATETIME, 
	generated_by INTEGER, 
	is_scheduled VARCHAR(10), 
	schedule VARCHAR(100), 
	recipients JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(generated_by) REFERENCES admin_users (id)
);
CREATE TABLE audit_retention_policies (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	entity_type VARCHAR(10), 
	action_type VARCHAR(18), 
	retention_days INTEGER NOT NULL, 
	action_after_expiry VARCHAR(50), 
	is_active VARCHAR(10), 
	created_at DATETIME, 
	updated_at DATETIME, 
	created_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(created_by) REFERENCES admin_users (id)
);
CREATE TABLE audit_statistics (
	id INTEGER NOT NULL, 
	date DATETIME NOT NULL, 
	total_actions INTEGER, 
	total_users INTEGER, 
	total_sessions INTEGER, 
	actions_by_type JSON, 
	actions_by_entity JSON, 
	top_users JSON, 
	failed_actions INTEGER, 
	error_types JSON, 
	avg_duration_ms INTEGER, 
	max_duration_ms INTEGER, 
	security_alerts INTEGER, 
	suspicious_activities JSON, 
	calculated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (date)
);
CREATE TABLE employee_notification_settings (
	id INTEGER NOT NULL, 
	admin_user_id INTEGER NOT NULL, 
	telegram_user_id VARCHAR(50) NOT NULL, 
	notifications_enabled BOOLEAN, 
	notification_language VARCHAR(10), 
	project_assigned BOOLEAN, 
	project_status_changed BOOLEAN, 
	project_deadline_reminder BOOLEAN, 
	project_overdue BOOLEAN, 
	project_new_task BOOLEAN, 
	avito_new_message BOOLEAN, 
	avito_unread_reminder BOOLEAN, 
	avito_urgent_message BOOLEAN, 
	lead_assigned BOOLEAN, 
	lead_status_changed BOOLEAN, 
	deal_assigned BOOLEAN, 
	deal_status_changed BOOLEAN, 
	work_hours_start VARCHAR(5), 
	work_hours_end VARCHAR(5), 
	weekend_notifications BOOLEAN, 
	urgent_notifications_always BOOLEAN, 
	avito_reminder_interval INTEGER, 
	project_reminder_interval INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (admin_user_id), 
	FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
);
CREATE TABLE notification_queue (
	id INTEGER NOT NULL, 
	telegram_user_id VARCHAR(50) NOT NULL, 
	admin_user_id INTEGER, 
	notification_type VARCHAR(50) NOT NULL, 
	priority VARCHAR(20), 
	title VARCHAR(200) NOT NULL, 
	message TEXT NOT NULL, 
	action_url VARCHAR(500), 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(100), 
	notification_metadata JSON, 
	status VARCHAR(20), 
	scheduled_at DATETIME, 
	sent_at DATETIME, 
	retry_count INTEGER, 
	max_retries INTEGER, 
	group_key VARCHAR(100), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
);
CREATE TABLE notification_log (
	id INTEGER NOT NULL, 
	telegram_user_id VARCHAR(50) NOT NULL, 
	admin_user_id INTEGER, 
	sent_by_user_id INTEGER, 
	notification_type VARCHAR(50) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	message TEXT NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	error_message TEXT, 
	telegram_message_id INTEGER, 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(100), 
	sent_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_user_id) REFERENCES admin_users (id), 
	FOREIGN KEY(sent_by_user_id) REFERENCES admin_users (id)
);
CREATE TABLE task_deadline_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    notification_type VARCHAR(50) NOT NULL,
                    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deadline_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
                );
INSERT INTO task_deadline_notifications VALUES(1,97,'daily_overdue','2025-10-30 18:05:08.335730','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(2,167,'daily_overdue','2025-10-30 18:05:08.725101','2025-10-23 13:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(3,171,'daily_overdue','2025-10-30 18:05:09.036844','2025-10-23 13:09:00.000000');
INSERT INTO task_deadline_notifications VALUES(4,175,'overdue','2025-10-30 18:05:09.400290','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(5,176,'daily_overdue','2025-10-30 18:05:09.764783','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(6,185,'24h_before','2025-10-30 18:05:10.103380','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(7,188,'daily_overdue','2025-10-30 18:05:10.423838','2025-10-25 18:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(8,96,'daily_overdue','2025-10-30 18:05:10.816786','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(9,182,'daily_overdue','2025-10-30 18:05:11.286451','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(10,166,'4h_before','2025-10-31 09:05:11.974299','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(11,172,'4h_before','2025-10-31 09:05:12.496151','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(12,166,'1h_before','2025-10-31 12:05:12.968395','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(13,172,'1h_before','2025-10-31 12:05:13.337617','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(14,166,'overdue','2025-10-31 15:05:13.951951','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(15,172,'overdue','2025-10-31 15:05:14.412343','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(16,175,'daily_overdue','2025-10-31 15:05:14.826713','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(17,97,'daily_overdue','2025-10-31 18:05:15.290687','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(18,167,'daily_overdue','2025-10-31 18:05:15.632170','2025-10-23 13:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(19,171,'daily_overdue','2025-10-31 18:05:15.968375','2025-10-23 13:09:00.000000');
INSERT INTO task_deadline_notifications VALUES(20,176,'daily_overdue','2025-10-31 18:05:16.332063','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(21,185,'overdue','2025-10-31 18:05:16.682437','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(22,188,'daily_overdue','2025-10-31 18:05:17.030976','2025-10-25 18:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(23,96,'daily_overdue','2025-10-31 18:05:17.388882','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(24,182,'daily_overdue','2025-10-31 18:05:17.768753','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(25,192,'overdue','2025-10-31 18:05:18.134164','2025-10-31 17:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(26,193,'overdue','2025-10-31 18:05:18.507080','2025-10-31 15:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(27,194,'4h_before','2025-11-01 12:09:43.138253','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(28,166,'daily_overdue','2025-11-01 13:13:33.678434','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(29,172,'daily_overdue','2025-11-01 13:13:34.028761','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(30,175,'daily_overdue','2025-11-01 15:20:23.961759','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(31,193,'daily_overdue','2025-11-01 15:25:45.692568','2025-10-31 15:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(32,194,'1h_before','2025-11-01 15:25:46.077255','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(33,194,'overdue','2025-11-01 16:40:35.022042','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(34,185,'daily_overdue','2025-11-01 17:28:32.219967','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(35,192,'daily_overdue','2025-11-01 17:28:32.580078','2025-10-31 17:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(36,97,'daily_overdue','2025-11-01 20:28:33.009057','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(37,167,'daily_overdue','2025-11-01 20:28:33.369146','2025-10-23 13:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(38,171,'daily_overdue','2025-11-01 20:28:33.694023','2025-10-23 13:09:00.000000');
INSERT INTO task_deadline_notifications VALUES(39,176,'daily_overdue','2025-11-01 20:28:34.018727','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(40,188,'daily_overdue','2025-11-01 20:28:34.353648','2025-10-25 18:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(41,96,'daily_overdue','2025-11-01 20:28:34.680249','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(42,182,'daily_overdue','2025-11-01 20:28:35.015513','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(43,166,'daily_overdue','2025-11-02 14:19:39.917497','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(44,172,'daily_overdue','2025-11-02 14:19:40.283560','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(45,175,'daily_overdue','2025-11-02 17:19:40.810084','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(46,193,'daily_overdue','2025-11-02 17:19:41.268773','2025-10-31 15:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(47,194,'daily_overdue','2025-11-02 17:19:41.663734','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(48,185,'daily_overdue','2025-11-02 20:19:42.246929','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(49,192,'daily_overdue','2025-11-02 20:19:42.697959','2025-10-31 17:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(50,97,'daily_overdue','2025-11-02 23:19:43.145482','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(51,171,'daily_overdue','2025-11-02 23:19:43.474682','2025-10-23 13:09:00.000000');
INSERT INTO task_deadline_notifications VALUES(52,176,'daily_overdue','2025-11-02 23:19:43.838552','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(53,188,'daily_overdue','2025-11-02 23:19:44.176199','2025-10-25 18:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(54,96,'daily_overdue','2025-11-02 23:19:44.522127','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(55,182,'daily_overdue','2025-11-02 23:19:44.854674','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(56,166,'daily_overdue','2025-11-03 14:19:45.560230','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(57,172,'daily_overdue','2025-11-03 14:19:45.913572','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(58,175,'daily_overdue','2025-11-03 17:19:46.409885','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(59,193,'daily_overdue','2025-11-03 17:19:46.810257','2025-10-31 15:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(60,194,'daily_overdue','2025-11-03 17:19:47.189527','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(61,185,'daily_overdue','2025-11-03 20:19:47.771873','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(62,192,'daily_overdue','2025-11-03 20:19:48.181183','2025-10-31 17:21:00.000000');
INSERT INTO task_deadline_notifications VALUES(63,97,'daily_overdue','2025-11-03 23:19:48.617004','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(64,171,'daily_overdue','2025-11-03 23:19:48.959435','2025-10-23 13:09:00.000000');
INSERT INTO task_deadline_notifications VALUES(65,176,'daily_overdue','2025-11-03 23:19:49.304635','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(66,188,'daily_overdue','2025-11-03 23:19:49.677805','2025-10-25 18:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(67,96,'daily_overdue','2025-11-03 23:19:50.000368','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(68,182,'daily_overdue','2025-11-03 23:19:50.351348','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(69,166,'daily_overdue','2025-11-04 14:19:51.061983','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(70,172,'daily_overdue','2025-11-04 14:19:51.447297','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(71,175,'daily_overdue','2025-11-04 17:19:51.958359','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(72,194,'daily_overdue','2025-11-04 17:19:52.321997','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(73,185,'daily_overdue','2025-11-04 20:19:52.791794','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(74,97,'daily_overdue','2025-11-04 23:19:53.247909','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(75,176,'daily_overdue','2025-11-04 23:19:53.584196','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(76,96,'daily_overdue','2025-11-04 23:19:53.912800','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(77,182,'daily_overdue','2025-11-04 23:19:54.241050','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(78,166,'daily_overdue','2025-11-05 14:19:54.947029','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(79,172,'daily_overdue','2025-11-05 14:19:55.361845','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(80,175,'daily_overdue','2025-11-05 17:19:55.973835','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(81,194,'daily_overdue','2025-11-05 17:19:56.465684','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(82,185,'daily_overdue','2025-11-05 20:19:56.892435','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(83,97,'daily_overdue','2025-11-05 23:19:57.375229','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(84,176,'daily_overdue','2025-11-05 23:19:57.713176','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(85,96,'daily_overdue','2025-11-05 23:19:58.045139','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(86,182,'daily_overdue','2025-11-05 23:19:58.379026','2025-10-27 12:40:00.000000');
INSERT INTO task_deadline_notifications VALUES(87,197,'4h_before','2025-11-06 08:19:58.970057','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(88,197,'1h_before','2025-11-06 11:19:59.495093','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(89,166,'daily_overdue','2025-11-06 14:19:59.912534','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(90,172,'daily_overdue','2025-11-06 14:20:00.347393','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(91,196,'overdue','2025-11-06 14:20:00.774912','2025-11-06 12:59:00.000000');
INSERT INTO task_deadline_notifications VALUES(92,197,'overdue','2025-11-06 14:20:01.150562','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(93,199,'overdue','2025-11-06 14:20:01.556820','2025-11-06 13:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(94,175,'daily_overdue','2025-11-06 17:20:02.031437','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(95,194,'daily_overdue','2025-11-06 17:20:02.413020','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(96,185,'daily_overdue','2025-11-06 20:20:02.859357','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(97,97,'daily_overdue','2025-11-06 23:20:03.252154','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(98,176,'daily_overdue','2025-11-06 23:20:03.587339','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(99,96,'daily_overdue','2025-11-06 23:20:03.924504','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(100,198,'24h_before','2025-11-07 11:20:04.810466','2025-11-08 11:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(101,166,'daily_overdue','2025-11-07 14:20:05.288565','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(102,172,'daily_overdue','2025-11-07 14:20:05.692669','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(103,196,'daily_overdue','2025-11-07 14:20:06.182182','2025-11-06 12:59:00.000000');
INSERT INTO task_deadline_notifications VALUES(104,197,'daily_overdue','2025-11-07 14:20:06.589485','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(105,199,'daily_overdue','2025-11-07 14:20:06.976016','2025-11-06 13:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(106,200,'overdue','2025-11-07 14:20:07.321573','2025-11-07 14:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(107,175,'daily_overdue','2025-11-07 17:20:07.773640','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(108,194,'daily_overdue','2025-11-07 17:20:08.148744','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(109,185,'daily_overdue','2025-11-07 20:20:08.635407','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(110,97,'daily_overdue','2025-11-07 23:20:09.139946','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(111,176,'daily_overdue','2025-11-07 23:20:09.497648','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(112,96,'daily_overdue','2025-11-07 23:20:09.836251','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(113,198,'4h_before','2025-11-08 08:20:10.593502','2025-11-08 11:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(114,166,'daily_overdue','2025-11-08 14:20:11.064174','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(115,172,'daily_overdue','2025-11-08 14:20:11.427473','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(116,196,'daily_overdue','2025-11-08 14:20:11.852767','2025-11-06 12:59:00.000000');
INSERT INTO task_deadline_notifications VALUES(117,197,'daily_overdue','2025-11-08 14:20:12.233069','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(118,198,'overdue','2025-11-08 14:20:12.588933','2025-11-08 11:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(119,199,'daily_overdue','2025-11-08 14:20:12.946610','2025-11-06 13:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(120,200,'daily_overdue','2025-11-08 14:20:13.285776','2025-11-07 14:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(121,175,'daily_overdue','2025-11-08 17:20:14.338125','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(122,203,'overdue','2025-11-08 17:20:14.727458','2025-11-08 16:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(123,194,'daily_overdue','2025-11-08 17:20:15.094523','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(124,185,'daily_overdue','2025-11-08 20:20:15.573031','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(125,195,'overdue','2025-11-08 20:20:15.948125','2025-11-08 18:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(126,97,'daily_overdue','2025-11-08 23:20:16.415451','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(127,176,'daily_overdue','2025-11-08 23:20:16.772445','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(128,96,'daily_overdue','2025-11-08 23:20:17.113597','2025-08-31 10:44:00.000000');
INSERT INTO task_deadline_notifications VALUES(129,166,'daily_overdue','2025-11-09 14:20:17.922289','2025-10-31 12:58:00.000000');
INSERT INTO task_deadline_notifications VALUES(130,169,'overdue','2025-11-09 14:20:18.287915','2025-11-09 13:05:00.000000');
INSERT INTO task_deadline_notifications VALUES(131,172,'daily_overdue','2025-11-09 14:20:18.630424','2025-10-31 13:11:00.000000');
INSERT INTO task_deadline_notifications VALUES(132,198,'daily_overdue','2025-11-09 14:20:19.000304','2025-11-08 11:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(133,196,'daily_overdue','2025-11-09 14:20:19.413076','2025-11-06 12:59:00.000000');
INSERT INTO task_deadline_notifications VALUES(134,197,'daily_overdue','2025-11-09 14:20:19.792501','2025-11-06 12:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(135,199,'daily_overdue','2025-11-09 14:20:20.126758','2025-11-06 13:30:00.000000');
INSERT INTO task_deadline_notifications VALUES(136,200,'daily_overdue','2025-11-09 14:20:20.468508','2025-11-07 14:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(137,175,'daily_overdue','2025-11-09 17:20:20.925519','2025-10-30 14:51:00.000000');
INSERT INTO task_deadline_notifications VALUES(138,203,'daily_overdue','2025-11-09 17:20:21.297122','2025-11-08 16:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(139,194,'daily_overdue','2025-11-09 17:20:21.638590','2025-11-01 16:37:00.000000');
INSERT INTO task_deadline_notifications VALUES(140,185,'daily_overdue','2025-11-09 20:20:22.129992','2025-10-31 17:24:00.000000');
INSERT INTO task_deadline_notifications VALUES(141,195,'daily_overdue','2025-11-09 20:20:22.554778','2025-11-08 18:56:00.000000');
INSERT INTO task_deadline_notifications VALUES(142,97,'daily_overdue','2025-11-09 23:20:23.034630','2025-08-24 11:00:00.000000');
INSERT INTO task_deadline_notifications VALUES(143,176,'daily_overdue','2025-11-09 23:20:23.375217','2025-10-26 14:55:00.000000');
INSERT INTO task_deadline_notifications VALUES(144,96,'daily_overdue','2025-11-09 23:20:23.720917','2025-08-31 10:44:00.000000');
CREATE TABLE hosting_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    client_name VARCHAR(255) NOT NULL,
                    client_company VARCHAR(255),
                    client_telegram_id BIGINT,

                    server_name VARCHAR(255) NOT NULL,
                    configuration TEXT,
                    ip_address VARCHAR(50),

                    cost_price REAL NOT NULL DEFAULT 0,
                    client_price REAL NOT NULL,
                    service_fee REAL DEFAULT 0,

                    start_date TIMESTAMP NOT NULL,
                    next_payment_date TIMESTAMP NOT NULL,
                    payment_period VARCHAR(20) DEFAULT 'monthly',

                    status VARCHAR(20) DEFAULT 'active',
                    notes TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, project_id INTEGER REFERENCES projects(id),

                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
                );
CREATE TABLE hosting_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,

                    amount REAL NOT NULL,
                    payment_date TIMESTAMP,
                    expected_date TIMESTAMP NOT NULL,

                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,

                    status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    receipt_url VARCHAR(500),

                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (server_id) REFERENCES hosting_servers (id) ON DELETE CASCADE
                );
CREATE TABLE project_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL UNIQUE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP,

                    unread_by_executor INTEGER DEFAULT 0,
                    unread_by_client INTEGER DEFAULT 0, is_pinned_by_owner BOOLEAN DEFAULT 0, is_hidden_by_owner BOOLEAN DEFAULT 0,

                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                );
INSERT INTO project_chats VALUES(1,36,'2025-11-01 12:12:33.229128','2025-11-01 12:12:33.229133',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(2,41,'2025-11-01 12:12:33.881235','2025-11-01 13:36:44.557615','2025-11-01 13:36:39.439623',0,0,0,0);
INSERT INTO project_chats VALUES(3,42,'2025-11-01 14:51:10.778453','2025-11-01 15:14:55.183671','2025-11-01 15:14:55.183659',1,0,0,0);
INSERT INTO project_chats VALUES(4,43,'2025-11-01 14:51:10.796284','2025-11-01 14:51:10.796287',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(5,44,'2025-11-01 14:51:10.798389','2025-11-01 14:51:10.798392',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(6,45,'2025-11-01 14:51:10.804753','2025-11-01 14:51:10.804756',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(7,1,'2025-11-01 15:30:24.883196','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(8,2,'2025-11-01 15:30:24.887666','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(9,3,'2025-11-01 15:30:24.888149','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(10,4,'2025-11-01 15:30:24.888545','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(11,5,'2025-11-01 15:30:24.888915','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(12,6,'2025-11-01 15:30:24.889289','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(13,7,'2025-11-01 15:30:24.889597','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(14,8,'2025-11-01 15:30:24.889915','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(15,9,'2025-11-01 15:30:24.890212','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(16,11,'2025-11-01 15:30:24.890538','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(17,12,'2025-11-01 15:30:24.890847','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(18,13,'2025-11-01 15:30:24.891161','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(19,14,'2025-11-01 15:30:24.891496','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(20,15,'2025-11-01 15:30:24.891748','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(21,16,'2025-11-01 15:30:24.892081','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(22,17,'2025-11-01 15:30:24.892482','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(23,18,'2025-11-01 15:30:24.892749','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(24,19,'2025-11-01 15:30:24.892993','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(25,20,'2025-11-01 15:30:24.893322','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(26,21,'2025-11-01 15:30:24.893579','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(27,22,'2025-11-01 15:30:24.893826','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(28,23,'2025-11-01 15:30:24.894071','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(29,24,'2025-11-01 15:30:24.894395','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(30,25,'2025-11-01 15:30:24.894641','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(31,26,'2025-11-01 15:30:24.894961','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(32,27,'2025-11-01 15:30:24.895188','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(33,28,'2025-11-01 15:30:24.895456','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(34,29,'2025-11-01 15:30:24.895726','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(35,30,'2025-11-01 15:30:24.895995','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(36,31,'2025-11-01 15:30:24.896236','2025-11-02 09:55:47.431512','2025-11-02 09:55:47.425936',0,1,0,0);
INSERT INTO project_chats VALUES(37,32,'2025-11-01 15:30:24.896498','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(38,33,'2025-11-01 15:30:24.896732','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(39,34,'2025-11-01 15:30:24.897012','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(40,35,'2025-11-01 15:30:24.897259','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(41,37,'2025-11-01 15:30:24.897512','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(42,38,'2025-11-01 15:30:24.897759','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(43,39,'2025-11-01 15:30:24.898054','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(44,40,'2025-11-01 15:30:24.898300','2025-11-01 15:30:24',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(45,46,'2025-11-01 15:30:24.898565','2025-11-02 09:31:33.019753','2025-11-02 09:30:06.250281',0,0,0,0);
INSERT INTO project_chats VALUES(46,47,'2025-11-02 10:47:06','2025-11-02 10:47:06',NULL,0,0,0,0);
INSERT INTO project_chats VALUES(47,48,'2025-11-02 10:49:52.452391','2025-11-02 16:00:17.725739','2025-11-02 16:00:01.237075',0,0,0,0);
CREATE TABLE project_chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,

                    sender_type VARCHAR(20) NOT NULL,
                    sender_id INTEGER,

                    message_text TEXT,
                    attachments TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read_by_executor BOOLEAN DEFAULT 0,
                    is_read_by_client BOOLEAN DEFAULT 0,
                    read_at TIMESTAMP,

                    has_contact_violation BOOLEAN DEFAULT 0,
                    violation_details TEXT,

                    related_revision_id INTEGER,

                    FOREIGN KEY (chat_id) REFERENCES project_chats (id) ON DELETE CASCADE,
                    FOREIGN KEY (related_revision_id) REFERENCES project_revisions (id)
                );
INSERT INTO project_chat_messages VALUES(1,2,'client',1,'привет','[]','2025-11-01 13:08:02.672915',1,1,'2025-11-01 13:24:11.473587',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(2,2,'executor',NULL,'здравствуйте','null','2025-11-01 13:35:54.149039',1,1,'2025-11-01 13:35:58.103483',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(3,2,'executor',NULL,NULL,'[{"filename": "\u041d2\u0413\u041f_\u0413\u041a_5_\u0420_\u041a\u041c2_1_\u0421\u0422_\u0421\u0445_\u0440\u0430\u0441\u043f_\u044d\u043b_\u043f\u043e\u043a\u0440\u044b\u0442\u0438\u044f_v9.pdf", "url": "/uploads/chat_attachments/405ba75d-d5b6-4be1-9a82-ec99133595a4.pdf", "size": 522690}]','2025-11-01 13:36:18.295967',1,1,'2025-11-01 13:36:44.557049',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(4,2,'executor',NULL,NULL,'[{"filename": "123123.png", "url": "/uploads/chat_attachments/0062e509-f405-47f0-bcef-f523af996fb6.png", "size": 2321126}]','2025-11-01 13:36:39.439429',1,1,'2025-11-01 13:36:44.557060',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(5,3,'client',11,'доброго','[]','2025-11-01 14:52:11.384541',1,1,'2025-11-01 14:52:24.080744',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(6,3,'executor',NULL,'как у тебя дела','null','2025-11-01 14:52:30.720697',1,1,'2025-11-01 14:52:33.342339',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(7,3,'client',11,'надо внести правки в бота','[]','2025-11-01 14:52:45.051340',1,1,'2025-11-01 14:52:45.506053',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(8,3,'client',11,'Привет','[]','2025-11-01 15:14:55.183403',0,1,NULL,0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(9,45,'client',11,'привет','[]','2025-11-01 15:36:08.676482',1,1,'2025-11-01 15:36:55.904589',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(10,45,'executor',NULL,'Доброго','null','2025-11-01 16:40:51.640622',1,1,'2025-11-01 17:03:06.738664',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(11,45,'client',11,NULL,'[]','2025-11-01 17:23:04.706984',1,1,'2025-11-02 08:15:40.102162',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(12,45,'client',11,NULL,'[]','2025-11-01 17:23:29.103396',1,1,'2025-11-02 08:15:40.102175',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(13,45,'client',11,NULL,'[]','2025-11-01 18:19:01.891572',1,1,'2025-11-02 08:15:40.102182',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(14,45,'client',11,NULL,'[]','2025-11-02 06:50:32.817096',1,1,'2025-11-02 08:15:40.102187',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(15,45,'client',11,NULL,'[]','2025-11-02 06:56:17.351296',1,1,'2025-11-02 08:15:40.102192',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(16,45,'client',11,NULL,'[]','2025-11-02 06:56:25.343169',1,1,'2025-11-02 08:15:40.102197',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(17,45,'client',11,NULL,'[]','2025-11-02 06:59:05.016539',1,1,'2025-11-02 08:15:40.102202',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(18,45,'client',11,NULL,'[]','2025-11-02 07:01:31.469870',1,1,'2025-11-02 08:15:40.102207',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(19,45,'client',11,NULL,'[]','2025-11-02 07:03:22.740095',1,1,'2025-11-02 08:15:40.102213',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(20,45,'client',11,NULL,'[]','2025-11-02 07:08:29.952508',1,1,'2025-11-02 08:15:40.102218',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(21,45,'client',11,NULL,'[]','2025-11-02 07:18:41.988715',1,1,'2025-11-02 08:15:40.102223',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(22,45,'client',11,NULL,'[]','2025-11-02 07:18:44.440483',1,1,'2025-11-02 08:15:40.102228',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(23,45,'client',11,NULL,'[]','2025-11-02 07:26:02.646103',1,1,'2025-11-02 08:15:40.102233',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(24,45,'client',11,NULL,'[]','2025-11-02 07:28:43.497105',1,1,'2025-11-02 08:15:40.102238',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(25,45,'client',11,NULL,'[]','2025-11-02 07:33:41.436818',1,1,'2025-11-02 08:15:40.102243',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(26,45,'client',11,NULL,'[]','2025-11-02 07:36:20.522098',1,1,'2025-11-02 08:15:40.102248',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(27,45,'client',11,'привет','[]','2025-11-02 07:52:03.908368',1,1,'2025-11-02 08:15:40.102253',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(28,45,'client',11,'как дела у тебя','[]','2025-11-02 07:52:09.689779',1,1,'2025-11-02 08:15:40.102259',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(29,45,'client',11,'ТЕСТ','[]','2025-11-02 08:21:34.772328',1,1,'2025-11-02 08:21:44.170173',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(30,45,'client',NULL,'🧪 АВТОМАТИЧЕСКОЕ ТЕСТОВОЕ СООБЩЕНИЕ - Проверка системы уведомлений! Если вы получили это уведомление - всё работает отлично!',NULL,'2025-11-02 09:28:50.824650',1,0,'2025-11-02 09:29:56.005007',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(31,45,'executor',NULL,'Один два раза','null','2025-11-02 09:30:06.249949',1,1,'2025-11-02 09:31:33.013986',0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(32,36,'executor',NULL,'123','null','2025-11-02 09:55:47.425700',1,0,NULL,0,NULL,NULL);
INSERT INTO project_chat_messages VALUES(33,47,'executor',NULL,'привет','null','2025-11-02 16:00:01.236704',1,1,'2025-11-02 16:00:17.723770',0,NULL,NULL);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('tasks',204);
INSERT INTO sqlite_sequence VALUES('task_comments',227);
INSERT INTO sqlite_sequence VALUES('roles',6);
INSERT INTO sqlite_sequence VALUES('permissions',45);
INSERT INTO sqlite_sequence VALUES('clients',44);
INSERT INTO sqlite_sequence VALUES('leads',7);
INSERT INTO sqlite_sequence VALUES('task_deadline_notifications',144);
INSERT INTO sqlite_sequence VALUES('project_chats',47);
INSERT INTO sqlite_sequence VALUES('project_chat_messages',33);
INSERT INTO sqlite_sequence VALUES('data_access_rules',5);
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
CREATE INDEX ix_admin_activity_logs_id ON admin_activity_logs (id);
CREATE INDEX ix_transactions_id ON transactions (id);
CREATE INDEX ix_expense_categories_id ON expense_categories (id);
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_inn ON clients(inn);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_client ON leads(client_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_client ON deals(client_id);
CREATE INDEX idx_deals_contract ON deals(contract_number);
CREATE INDEX idx_documents_number ON documents(number);
CREATE INDEX idx_documents_client ON documents(client_id);
CREATE INDEX idx_documents_deal ON documents(deal_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_module ON permissions(module);
CREATE INDEX ix_audit_log_user_id ON audit_log (user_id);
CREATE INDEX ix_audit_log_entity_type ON audit_log (entity_type);
CREATE INDEX ix_audit_log_action_type ON audit_log (action_type);
CREATE INDEX ix_audit_log_timestamp ON audit_log (timestamp);
CREATE INDEX idx_audit_action_entity ON audit_log (action_type, entity_type);
CREATE INDEX ix_employee_notification_settings_telegram_user_id ON employee_notification_settings (telegram_user_id);
CREATE INDEX ix_employee_notification_settings_id ON employee_notification_settings (id);
CREATE INDEX ix_notification_queue_telegram_user_id ON notification_queue (telegram_user_id);
CREATE INDEX ix_notification_queue_id ON notification_queue (id);
CREATE INDEX ix_notification_queue_group_key ON notification_queue (group_key);
CREATE INDEX ix_notification_log_telegram_user_id ON notification_log (telegram_user_id);
CREATE INDEX ix_notification_log_id ON notification_log (id);
CREATE INDEX idx_admin_users_telegram_id 
                        ON admin_users(telegram_id)
                    ;
CREATE INDEX idx_task_deadline_notifications_task_id
                ON task_deadline_notifications(task_id)
            ;
CREATE INDEX idx_task_deadline_notifications_type
                ON task_deadline_notifications(task_id, notification_type)
            ;
CREATE INDEX idx_task_deadline_notifications_sent_at
                ON task_deadline_notifications(sent_at)
            ;
CREATE INDEX idx_hosting_servers_client_id ON hosting_servers(client_id)
            ;
CREATE INDEX idx_hosting_servers_status ON hosting_servers(status)
            ;
CREATE INDEX idx_hosting_servers_next_payment ON hosting_servers(next_payment_date)
            ;
CREATE INDEX idx_hosting_payments_server_id ON hosting_payments(server_id)
            ;
CREATE INDEX idx_hosting_payments_status ON hosting_payments(status)
            ;
CREATE INDEX idx_hosting_payments_expected_date ON hosting_payments(expected_date)
            ;
CREATE INDEX idx_hosting_servers_project_id
                ON hosting_servers(project_id)
            ;
CREATE UNIQUE INDEX idx_project_chats_project_id
                ON project_chats(project_id)
            ;
CREATE INDEX idx_project_chat_messages_chat_id
                ON project_chat_messages(chat_id)
            ;
CREATE INDEX idx_project_chat_messages_created_at
                ON project_chat_messages(created_at)
            ;
COMMIT;
