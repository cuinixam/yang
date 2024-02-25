from pathlib import Path
from typing import List

from py_app_dev.core.logging import logger

from yanga.cmake.builder import CMakeBuildSystemGenerator
from yanga.cmake.runner import CMakeRunner
from yanga.domain.execution_context import ExecutionContext
from yanga.domain.pipeline import PipelineStep


class GenerateBuildSystemFiles(PipelineStep):
    def __init__(self, execution_context: ExecutionContext, output_dir: Path) -> None:
        super().__init__(execution_context, output_dir)
        self.logger = logger.bind()
        self.generated_files: List[Path] = []

    def get_name(self) -> str:
        return self.__class__.__name__

    def run(self) -> int:
        self.logger.info(f"Run {self.__class__.__name__} stage. Output dir: {self.output_dir}")
        generated_files = CMakeBuildSystemGenerator(self.execution_context, self.output_dir).generate()
        for file in generated_files:
            file.to_file()
        self.generated_files = [file.path for file in generated_files]
        return 0

    def get_inputs(self) -> List[Path]:
        return self.execution_context.user_config_files

    def get_outputs(self) -> List[Path]:
        return self.generated_files

    def update_execution_context(self) -> None:
        pass


class ExecuteBuild(PipelineStep):
    """This step is always executed. The dependencies are handled by the build system itself."""

    def __init__(self, execution_context: ExecutionContext, output_dir: Path) -> None:
        super().__init__(execution_context, output_dir)
        self.logger = logger.bind()

    def get_name(self) -> str:
        return self.__class__.__name__

    def run(self) -> int:
        self.logger.debug(f"Run {self.get_name()} stage. Output dir: {self.output_dir}")
        CMakeRunner(self.execution_context.install_dirs).run(
            self.output_dir, self.execution_context.user_request.target_name
        )
        return 0

    def get_inputs(self) -> List[Path]:
        return []

    def get_outputs(self) -> List[Path]:
        return []

    def update_execution_context(self) -> None:
        pass
