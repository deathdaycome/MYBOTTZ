import os
import tempfile
import asyncio
from typing import Optional
from telegram import Voice, Bot
import speech_recognition as sr
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from ..config.settings import settings
from ..config.logging import get_logger, log_api_call

logger = get_logger(__name__)

class SpeechService:
    """Улучшенный сервис для распознавания русской речи"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.max_duration = 300  # Максимальная длительность 5 минут
        self.supported_languages = ['ru-RU', 'en-US']
        
        # Оптимизированные настройки для русского языка
        self.recognizer.energy_threshold = 200  # Понижено для лучшей чувствительности
        self.recognizer.pause_threshold = 1.0   # Увеличено для русской речи
        self.recognizer.non_speaking_duration = 0.8
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
    
    async def process_voice_message(self, voice: Voice, bot: Bot) -> Optional[str]:
        """Обработка голосового сообщения из Telegram с фокусом на русском языке"""
        try:
            logger.info(f"Начинаем обработку голосового сообщения: {voice.duration}s, {voice.file_size} bytes")
            
            # Проверяем длительность
            if voice.duration > self.max_duration:
                logger.warning(f"Голосовое сообщение слишком длинное: {voice.duration}s")
                return None
            
            # Скачиваем голосовое сообщение
            voice_data = await self._download_voice(voice, bot)
            if not voice_data:
                logger.error("Не удалось скачать голосовое сообщение")
                return None
            
            # Конвертируем в WAV с оптимизацией для речи
            wav_data = await self._convert_to_wav_optimized(voice_data)
            if not wav_data:
                logger.error("Не удалось конвертировать в WAV")
                return None
            
            # Распознаем речь с множественными попытками
            text = await self._recognize_speech_multi_attempt(wav_data)
            
            if text:
                logger.info(f"Речь распознана успешно: {len(text)} символов - '{text[:100]}...'")
                return self._post_process_text(text)
            else:
                logger.warning("Не удалось распознать речь")
                return None
            
        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}")
            return None
    
    async def _download_voice(self, voice: Voice, bot: Bot) -> Optional[bytes]:
        """Скачивание голосового сообщения"""
        try:
            file = await bot.get_file(voice.file_id)
            file_content = await file.download_as_bytearray()
            
            log_api_call("Telegram", "download_voice", True)
            logger.info(f"Голосовое сообщение скачано: {len(file_content)} bytes")
            
            return bytes(file_content)
            
        except Exception as e:
            log_api_call("Telegram", "download_voice", False)
            logger.error(f"Ошибка при скачивании голосового сообщения: {e}")
            return None
    
    async def _convert_to_wav_optimized(self, voice_data: bytes) -> Optional[bytes]:
        """Конвертация аудио в WAV формат с оптимизацией для распознавания речи"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as input_file:
                input_file.write(voice_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as output_file:
                output_path = output_file.name
            
            try:
                # Загружаем OGG файл
                audio = AudioSegment.from_file(input_path, format="ogg")
                logger.info(f"Исходное аудио: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} каналов")
                
                # Оптимизируем для распознавания речи
                # Конвертируем в моно
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                
                # Устанавливаем оптимальную частоту дискретизации для Google Speech API
                audio = audio.set_frame_rate(16000)
                
                # Устанавливаем разрядность
                audio = audio.set_sample_width(2)  # 16-bit
                
                # Нормализуем громкость
                audio = audio.normalize()
                
                # Убираем тишину в начале и конце
                # Убираем тишину в начале и конце (исправленная версия)
                try:
                    audio = audio.strip_silence(silence_thresh=-40, silence_len=300)
                except TypeError:
                    # Если strip_silence не поддерживает seek_step, используем без него
                    audio = audio.strip_silence()
                except Exception as e:
                    # Если strip_silence совсем не работает, пропускаем
                    logger.debug(f"Не удалось убрать тишину: {e}")
                
                # Применяем фильтр высоких частот для улучшения качества речи
                audio = audio.high_pass_filter(80)
                
                # Компрессия для выравнивания громкости
                audio = audio.compress_dynamic_range(threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
                
                logger.info(f"Обработанное аудио: {len(audio)}ms, {audio.frame_rate}Hz")
                
                # Экспортируем в WAV
                audio.export(output_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                
                # Читаем результат
                with open(output_path, 'rb') as f:
                    wav_data = f.read()
                
                logger.info(f"WAV файл создан: {len(wav_data)} bytes")
                return wav_data
                
            finally:
                # Удаляем временные файлы
                for path in [input_path, output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
            
        except Exception as e:
            logger.error(f"Ошибка при конвертации аудио: {e}")
            return None
    
    async def _recognize_speech_multi_attempt(self, wav_data: bytes) -> Optional[str]:
        """Распознавание речи с множественными попытками и разными настройками"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(wav_data)
                temp_path = temp_file.name
            
            try:
                results = []
                
                # Попытка 1: Стандартные настройки для русского языка
                result1 = await self._attempt_recognition(temp_path, "ru-RU", adjust_noise=True)
                if result1:
                    results.append(("standard_ru", result1))
                
                # Попытка 2: Более чувствительные настройки
                result2 = await self._attempt_recognition(temp_path, "ru-RU", adjust_noise=False, energy_threshold=100)
                if result2:
                    results.append(("sensitive_ru", result2))
                
                # Попытка 3: С предварительной обработкой шума
                result3 = await self._attempt_recognition(temp_path, "ru-RU", adjust_noise=True, noise_duration=1.0)
                if result3:
                    results.append(("noise_adjusted_ru", result3))
                
                # Попытка 4: Английский язык как запасной вариант
                result4 = await self._attempt_recognition(temp_path, "en-US", adjust_noise=True)
                if result4:
                    results.append(("english", result4))
                
                # Попытка 5: Без указания языка (автоопределение)
                result5 = await self._attempt_recognition(temp_path, None, adjust_noise=True)
                if result5:
                    results.append(("auto", result5))
                
                # Выбираем лучший результат
                if results:
                    # Приоритет русскому языку
                    for method, text in results:
                        if method.startswith(("standard_ru", "sensitive_ru", "noise_adjusted_ru")) and len(text.strip()) >= 10:
                            logger.info(f"Выбран результат метода {method}: {text}")
                            return text
                    
                    # Если русский не сработал, берем любой результат длиннее 10 символов
                    for method, text in results:
                        if len(text.strip()) >= 10:
                            logger.info(f"Выбран результат метода {method}: {text}")
                            return text
                    
                    # Если все результаты короткие, берем самый длинный
                    best_result = max(results, key=lambda x: len(x[1]))
                    logger.info(f"Выбран самый длинный результат {best_result[0]}: {best_result[1]}")
                    return best_result[1]
                
                return None
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {e}")
            return None
    
    async def _attempt_recognition(self, audio_path: str, language: str = None, 
                                 adjust_noise: bool = True, noise_duration: float = 0.5,
                                 energy_threshold: int = None) -> Optional[str]:
        """Одна попытка распознавания с заданными параметрами"""
        try:
            # Создаем новый экземпляр recognizer для изоляции настроек
            recognizer = sr.Recognizer()
            
            if energy_threshold:
                recognizer.energy_threshold = energy_threshold
            else:
                recognizer.energy_threshold = 200
            
            recognizer.pause_threshold = 1.0
            recognizer.non_speaking_duration = 0.8
            recognizer.dynamic_energy_threshold = True
            
            with sr.AudioFile(audio_path) as source:
                # Настройка шумоподавления
                if adjust_noise:
                    recognizer.adjust_for_ambient_noise(source, duration=noise_duration)
                
                # Записываем аудио
                audio_data = recognizer.record(source)
            
            # Распознавание с указанным языком или без
            if language:
                if language == "ru-RU":
                    # Для русского языка пробуем разные варианты
                    try:
                        return recognizer.recognize_google(audio_data, language="ru-RU")
                    except:
                        try:
                            return recognizer.recognize_google(audio_data, language="ru")
                        except:
                            return recognizer.recognize_google(audio_data, language="ru-RU", show_all=False)
                else:
                    return recognizer.recognize_google(audio_data, language=language)
            else:
                return recognizer.recognize_google(audio_data)
                
        except sr.UnknownValueError:
            # Речь не распознана - это нормально
            return None
        except sr.RequestError as e:
            logger.warning(f"Ошибка запроса к Google Speech API: {e}")
            return None
        except Exception as e:
            logger.warning(f"Ошибка в попытке распознавания: {e}")
            return None
    
    def _post_process_text(self, text: str) -> str:
        """Постобработка распознанного текста"""
        try:
            # Убираем лишние пробелы
            text = ' '.join(text.split())
            
            # Исправляем регистр
            if text:
                text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
            
            # Удаляем повторяющиеся знаки препинания
            import re
            text = re.sub(r'[.]{2,}', '.', text)
            text = re.sub(r'[,]{2,}', ',', text)
            text = re.sub(r'[!]{2,}', '!', text)
            text = re.sub(r'[?]{2,}', '?', text)
            
            # Добавляем точку в конце если её нет
            if text and text[-1] not in '.!?':
                text += '.'
            
            logger.info(f"Постобработка завершена: '{text}'")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при постобработке текста: {e}")
            return text
    
    async def get_audio_info(self, voice_data: bytes) -> dict:
        """Получение детальной информации об аудио"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(voice_data)
                temp_path = temp_file.name
            
            try:
                audio = AudioSegment.from_file(temp_path, format="ogg")
                
                return {
                    'duration': len(audio) / 1000.0,
                    'frame_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'sample_width': audio.sample_width,
                    'max_amplitude': audio.max,
                    'rms': audio.rms,
                    'format': 'ogg',
                    'file_size': len(voice_data)
                }
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации об аудио: {e}")
            return {}
    
    def is_voice_supported(self, voice: Voice) -> bool:
        """Расширенная проверка поддержки голосового сообщения"""
        # Проверяем длительность (максимум 5 минут)
        if voice.duration > self.max_duration:
            logger.warning(f"Голосовое сообщение слишком длинное: {voice.duration}s")
            return False
        
        # Проверяем минимальную длительность (минимум 1 секунда)
        if voice.duration < 1:
            logger.warning(f"Голосовое сообщение слишком короткое: {voice.duration}s")
            return False
        
        # Проверяем размер файла (максимум 50MB)
        if voice.file_size and voice.file_size > 50 * 1024 * 1024:
            logger.warning(f"Файл слишком большой: {voice.file_size} bytes")
            return False
        
        return True

# Создаем глобальный экземпляр сервиса
speech_service = SpeechService()

# Функция-обертка для удобства использования
async def process_voice_message(voice: Voice, bot: Bot) -> Optional[str]:
    """Обработка голосового сообщения (функция-обертка)"""
    return await speech_service.process_voice_message(voice, bot)