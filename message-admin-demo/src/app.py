# src/app.py
import gradio as gr
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import logging

from src.config import settings
from src.validation import conf_validator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Глобальные переменные ---
kafka_producer = None
initialization_error = None
topics_list = []

# --- Инициализация ---
try:
    # 1. Валидация конфигурации топиков
    conf_validator.validate()
    topics_list = conf_validator.topics
    if not topics_list:
        raise ValueError("No topics found in the configuration file.")

    # 2. Попытка подключения к Kafka
    logger.info(
        f"Attempting to connect to Kafka at {settings.broker.kafka_bootstrap_servers}"
    )
    kafka_producer = KafkaProducer(
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        # Устанавливаем небольшой таймаут, чтобы приложение не зависало надолго при старте
        request_timeout_ms=5000,
    )
    # Проверка соединения (опционально, но полезно)
    kafka_producer.bootstrap_connected()
    logger.info("Successfully connected to Kafka.")

except (NoBrokersAvailable, ValueError) as e:
    error_message = f"Failed to connect to Kafka or validate config: {e}"
    logger.error(error_message)
    initialization_error = error_message
except Exception as e:
    error_message = f"An unexpected error occurred during initialization: {e}"
    logger.error(error_message)
    initialization_error = error_message


# --- Функции для Gradio ---
def send_kafka_message(topic, message):
    """Отправляет сообщение в указанный топик Kafka."""
    if kafka_producer is None:
        return f"Error: Kafka producer is not available. Reason: {initialization_error}"

    if not message:
        return "Warning: Message is empty. Nothing was sent."

    try:
        future = kafka_producer.send(topic, {"message": message})
        # Ожидаем подтверждения отправки
        record_metadata = future.get(timeout=10)
        logger.info(
            f"Message sent to topic '{record_metadata.topic}' partition {record_metadata.partition}"
        )
        return f"Message successfully sent to topic: {topic}"
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {e}")
        return f"Error sending message to Kafka: {e}"


# --- Создание интерфейса Gradio ---
def create_gradio_app():
    """Создает и возвращает Gradio-приложение."""
    with gr.Blocks(title="Kafka Message Sender",) as demo:
        gr.Markdown("# Kafka Message Sender")

        if initialization_error:
            # Если есть ошибка инициализации, показываем только ее
            gr.Markdown(f"## ⚠️ Application failed to start!")
            gr.Textbox(
                value=initialization_error,
                label="Error Details",
                interactive=False,
                max_lines=5,
            )
        else:
            # Если все хорошо, показываем основной интерфейс
            with gr.Row():
                topic_dropdown = gr.Dropdown(
                    choices=topics_list,
                    label="Select Kafka Topic",
                    value=topics_list[0] if topics_list else None,
                )

            message_input = gr.Textbox(
                lines=5, label="Message", placeholder="Type your message here..."
            )

            send_button = gr.Button("Send Message")

            output_text = gr.Textbox(label="Result", interactive=False)

            send_button.click(
                fn=send_kafka_message,
                inputs=[topic_dropdown, message_input],
                outputs=output_text,
            )

    return demo


app = create_gradio_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
