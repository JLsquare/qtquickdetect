import ultralytics
import logging


def load_model(model_path, device) -> ultralytics.YOLO:
    """
    Loads the model from the given path.

    :param model_path: Path to the model.
    :param device: Device to load the model on.
    :return: Loaded model.
    """
    try:
        model = ultralytics.YOLO(model_path).to(device)
        if model.task != 'detect':
            raise ValueError(f'Model task ({model.task}) does not match pipeline task')
        return model
    except Exception as e:
        logging.error(f'Failed to load model: {e}')
        raise e
