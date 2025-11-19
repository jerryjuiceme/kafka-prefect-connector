# src/app.py
import gradio as gr
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import logging

from src.config import settings
from src.validation import conf_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global variables ---
kafka_producer = None
initialization_error = None
topics_list = []


try:
    # 1. Validate topic configuration
    conf_validator.validate()
    topics_list = conf_validator.topics
    if not topics_list:
        raise ValueError("No topics found in the configuration file.")

    # 2. Attempt to connect to Kafka
    logger.info(
        "Attempting to connect to Kafka at %s",
        settings.broker.kafka_bootstrap_servers,
    )
    kafka_producer = KafkaProducer(
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        # Set a short timeout so the app doesn't hang for too long on startup
        request_timeout_ms=5000,
    )
    # Check connection (optional but useful)
    kafka_producer.bootstrap_connected()
    logger.info("Successfully connected to Kafka.")

except (NoBrokersAvailable, ValueError) as e:
    error_message = "Failed to connect to Kafka or validate config: %s" % e
    logger.error(error_message)
    initialization_error = error_message
except Exception as e:
    error_message = "An unexpected error occurred during initialization: %s" % e
    logger.error(error_message)
    initialization_error = error_message


# --- Functions for Gradio ---
def send_kafka_message(topic, message):
    """Sends a message to the specified Kafka topic."""
    if kafka_producer is None:
        return (
            "Error: Kafka producer is not available. Reason: %s",
            initialization_error,
        )

    if not message:
        return "Warning: Message is empty. Nothing was sent."

    try:
        future = kafka_producer.send(topic, {"message": message})
        # Wait for send confirmation
        record_metadata = future.get(timeout=10)
        logger.info(
            "Message sent to topic '%s'" % topic,
        )
        return f"Message successfully sent to topic: {topic}"
    except Exception as e:
        logger.error("Failed to send message to Kafka: %s" % e)
        return f"Error sending message to Kafka: {e}"


# --- Create Gradio interface ---
def create_gradio_app():
    """Creates and returns the Gradio application."""
    with gr.Blocks(
        title="Kafka Message Sender",
        theme=gr.themes.Soft(),  # type: ignore
        css="""
        .container { margin: auto; position: relative; } }
        """,
    ) as demo:
        gr.Markdown("# Kafka Message Sender")
        gr.Markdown("### Demo panel for Kafka -> Prefect trigger")

        if initialization_error:
            gr.Markdown("## Application failed to start!")
            gr.Textbox(
                value=initialization_error,
                label="Error Details",
                interactive=False,
                max_lines=10,
            )
        else:
            with gr.Row():

                with gr.Column(scale=1, min_width=250, variant="compact"):
                    topic_dropdown = gr.Dropdown(
                        choices=topics_list,
                        label="Select Kafka Topic",
                        value=topics_list[0] if topics_list else None,
                        container=True,
                    )

            with gr.Column(scale=3, variant="compact"):
                gr.Markdown("### Send message")
                message_input = gr.Textbox(
                    lines=8,
                    label="Message",
                    placeholder="Enter your message here...",
                    container=True,
                )

                with gr.Row():
                    send_button = gr.Button(
                        "Send Message", variant="primary", size="lg"
                    )
                    clear_button = gr.Button("Clear", variant="secondary")

                output_text = gr.Textbox(
                    label="Result",
                    interactive=False,
                    lines=3,
                )

            send_button.click(
                fn=send_kafka_message,
                inputs=[topic_dropdown, message_input],
                outputs=output_text,
            )
            clear_button.click(
                fn=lambda: ("", ""),
                inputs=None,
                outputs=[message_input, output_text],
            )

    return demo


app = create_gradio_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
