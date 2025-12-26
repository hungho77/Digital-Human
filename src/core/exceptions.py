"""Custom exceptions for the pipeline framework."""


class PipelineException(Exception):
    """Base exception for pipeline errors"""

    pass


class ProcessorException(PipelineException):
    """Exception raised by a processor"""

    def __init__(self, processor_name: str, message: str):
        self.processor_name = processor_name
        super().__init__(f"[{processor_name}] {message}")


class TransportException(PipelineException):
    """Exception raised by a transport"""

    pass


class ServiceException(PipelineException):
    """Exception raised by a service (TTS, LLM, ASR, etc.)"""

    pass


class AvatarException(PipelineException):
    """Exception raised during avatar generation"""

    pass
