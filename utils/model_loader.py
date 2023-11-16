from models.app_state import AppState
import ultralytics
import logging

appstate = AppState.get_instance()


def load_model(model_path) -> ultralytics.YOLO:
    """
    Loads the model from the given path.

    :param model_path: Path to the model.
    :return: Loaded model.
    """
    try:
        model = ultralytics.YOLO(model_path).to(appstate.device)
        if model.task != 'detect':
            raise ValueError(f'Model task ({model.task}) does not match pipeline task')
        return model
    except Exception as e:
        logging.error(f'Failed to load model: {e}')
        raise e
