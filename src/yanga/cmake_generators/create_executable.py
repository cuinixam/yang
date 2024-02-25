from pathlib import Path
from typing import List, Optional
from .generator import CMakeGenerator


from yanga.domain.component_analyzer import ComponentAnalyzer
from yanga.domain.execution_context import (
    ExecutionContext,
    UserRequest,
    UserRequestScope,
    UserRequestTarget,
    UserVariantRequest,
)

from .cmake_backend import (
    CMakeAddExecutable,
    CMakeComment,
    CMakeCustomTarget,
    CMakeElement,
    CMakeIncludeDirectories,
    CMakeObjectLibrary,
    CMakePath,
)


class CreateExecutableCMakeGenerator(CMakeGenerator):
    """Generates CMake elements to build an executable for a variant."""

    def __init__(self, execution_context: ExecutionContext, output_dir: Path) -> None:
        super().__init__(execution_context, output_dir)

    @property
    def variant_name(self) -> Optional[str]:
        return self.execution_context.variant_name

    def generate(self) -> List[CMakeElement]:
        elements = []
        elements.append(CMakeComment(f"Generated by {self.__class__.__name__}"))
        elements.extend(self.create_variant_cmake_elements())
        elements.extend(self.create_components_cmake_elements())
        return elements

    def create_variant_cmake_elements(self) -> List[CMakeElement]:
        elements = []
        elements.append(self.get_include_directories())
        # TODO: I do not like that I have to know here that the components are object libraries
        variant_executable = CMakeAddExecutable(
            "${PROJECT_NAME}",
            sources=[],
            libraries=[
                CMakeObjectLibrary(component.name).target_name for component in self.execution_context.components
            ],
        )

        elements.append(variant_executable)
        elements.append(
            CMakeCustomTarget(
                UserVariantRequest(self.variant_name, UserRequestTarget.BUILD).target_name,
                f"Build variant {self.variant_name}",
                [],
                [variant_executable.name],
            )
        )
        return elements

    def get_include_directories(self) -> CMakeIncludeDirectories:
        collector = ComponentAnalyzer(
            self.execution_context.components, self.execution_context.create_artifacts_locator()
        )
        include_dirs = collector.collect_include_directories() + self.execution_context.include_directories
        return CMakeIncludeDirectories([CMakePath(path) for path in include_dirs])

    def create_components_cmake_elements(self) -> List[CMakeElement]:
        elements = []
        for component in self.execution_context.components:
            component_analyzer = ComponentAnalyzer([component], self.execution_context.create_artifacts_locator())
            component_library = CMakeObjectLibrary(component.name, component_analyzer.collect_sources())
            elements.append(component_library)
            elements.append(
                CMakeCustomTarget(
                    UserRequest(
                        UserRequestScope.COMPONENT, self.variant_name, component.name, UserRequestTarget.COMPILE
                    ).target_name,
                    f"Compile component {component.name}",
                    [],
                    [component_library.target_name],
                )
            )
        return elements
