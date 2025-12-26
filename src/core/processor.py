"""Base frame processor implementation."""

from abc import ABC, abstractmethod
from asyncio import Queue, create_task, CancelledError
from typing import Optional
from src.core.frames import Frame, SystemFrame, ErrorFrame
from src.utils.logger import logger


class FrameProcessor(ABC):
    """Base processor for frame-based pipelines (Pipecat-style)"""

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self._prev: Optional[FrameProcessor] = None
        self._next: Optional[FrameProcessor] = None

        # Dual-queue system: priority for system frames
        self._input_queue: Queue = Queue()
        self._system_queue: Queue = Queue()

        # Processing control
        self._processing_task = None
        self._running = False

    def link(self, next_processor: "FrameProcessor") -> "FrameProcessor":
        """Link this processor to the next one in the chain"""
        self._next = next_processor
        next_processor._prev = self
        logger.debug(f"{self.name} -> {next_processor.name}")
        return next_processor

    async def queue_frame(self, frame: Frame):
        """Queue a frame for processing (called by previous processor)"""
        if isinstance(frame, SystemFrame):
            await self._system_queue.put(frame)
        else:
            await self._input_queue.put(frame)

    async def push_frame(self, frame: Frame):
        """Push frame to next processor (called after processing)"""
        if self._next:
            await self._next.queue_frame(frame)
        else:
            logger.debug(f"{self.name}: No next processor, dropping frame {frame.type}")

    async def push_error(self, error: Exception):
        """Push error upstream"""
        error_frame = ErrorFrame(error=error, source=self.name)
        if self._prev:
            await self._prev.queue_frame(error_frame)
        else:
            logger.error(f"{self.name}: Error with no upstream handler: {error}")

    @abstractmethod
    async def process_frame(self, frame: Frame):
        """
        Process a single frame (override in subclasses)

        Common patterns:
        1. Transform: modify frame and push
        2. Filter: conditionally push or drop
        3. Generate: create new frames and push
        4. Sink: consume frame without pushing
        """
        pass

    async def process(self):
        """Main processing loop"""
        self._running = True
        logger.info(f"{self.name}: Started processing")

        try:
            while self._running:
                # Process system frames first (priority)
                if not self._system_queue.empty():
                    frame = await self._system_queue.get()
                else:
                    frame = await self._input_queue.get()

                try:
                    await self.process_frame(frame)
                except Exception as e:
                    logger.error(f"{self.name}: Error processing frame: {e}")
                    await self.push_error(e)

        except CancelledError:
            logger.info(f"{self.name}: Processing cancelled")
        finally:
            self._running = False
            logger.info(f"{self.name}: Stopped processing")

    async def start(self):
        """Start the processor"""
        if not self._processing_task:
            self._processing_task = create_task(self.process())

    async def stop(self):
        """Stop the processor"""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except CancelledError:
                pass
