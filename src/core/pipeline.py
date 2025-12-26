"""Pipeline orchestration for processor chains."""

from typing import List
import asyncio
from src.core.processor import FrameProcessor
from src.core.frames import StartFrame, EndFrame
from src.utils.logger import logger


class Pipeline:
    """Orchestrates processor chains (Pipecat-style)"""

    def __init__(self, processors: List[FrameProcessor], name: str = "Pipeline"):
        self.name = name
        self.processors = processors
        self._link_processors()
        self._running = False

    def _link_processors(self):
        """Chain processors together"""
        for i in range(len(self.processors) - 1):
            self.processors[i].link(self.processors[i + 1])

    async def start(self):
        """Start all processors and send start frame"""
        logger.info(
            f"{self.name}: Starting pipeline with {len(self.processors)} processors"
        )

        # Start all processors
        for processor in self.processors:
            await processor.start()

        # Send start frame
        await self.processors[0].queue_frame(StartFrame())

        self._running = True
        logger.info(f"{self.name}: Pipeline started")

    async def stop(self):
        """Stop pipeline"""
        if not self._running:
            return

        logger.info(f"{self.name}: Stopping pipeline")

        # Send end frame
        await self.processors[0].queue_frame(EndFrame())

        # Stop all processors
        for processor in self.processors:
            await processor.stop()

        self._running = False
        logger.info(f"{self.name}: Pipeline stopped")

    async def run(self):
        """Start and wait for pipeline to complete"""
        await self.start()
        # Wait for all processor tasks
        await asyncio.gather(*[p._processing_task for p in self.processors])
