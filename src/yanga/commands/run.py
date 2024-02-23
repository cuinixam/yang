from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from typing import Optional

from py_app_dev.core.cmd_line import Command, register_arguments_for_config_dataclass
from py_app_dev.core.exceptions import UserNotificationException
from py_app_dev.core.logging import logger, time_it

from yanga.domain.execution_context import UserRequest, UserRequestScope
from yanga.domain.project_slurper import YangaProjectSlurper
from yanga.yrun.pipeline import PipelineScheduler, PipelineStepsExecutor

from .base import CommandConfigBase, CommandConfigFactory, prompt_user_to_select_option

# TODO: Refactor this and the build command to avoid code duplication


@dataclass
class RunCommandConfig(CommandConfigBase):
    variant_name: Optional[str] = field(
        default=None, metadata={"help": "SPL variant name. If none is provided, it will prompt to select one."}
    )
    component_name: Optional[str] = field(
        default=None, metadata={"help": "Restrict the scope to one specific component."}
    )
    target: Optional[str] = field(default=None, metadata={"help": "Define a specific target to execute."})
    step: Optional[str] = field(
        default=None, metadata={"help": "Name of the step to run (as written in the pipeline config)."}
    )
    single: bool = field(
        default=False,
        metadata={
            "help": "If provided, only the provided step will run,"
            " without running all previous steps in the pipeline.",
            "action": "store_true",
        },
    )
    print: bool = field(
        default=False,
        metadata={
            "help": "Print the pipeline steps.",
            "action": "store_true",
        },
    )
    force_run: bool = field(
        default=False,
        metadata={
            "help": "Force the execution of a step even if it is not dirty.",
            "action": "store_true",
        },
    )


class RunCommand(Command):
    def __init__(self) -> None:
        super().__init__("run", "Run a yanga pipeline step (and all previous steps if necessary).")
        self.logger = logger.bind()

    @time_it("Run")
    def run(self, args: Namespace) -> int:
        self.logger.debug(f"Running {self.name} with args {args}")
        self.do_run(CommandConfigFactory.create_config(RunCommandConfig, args))
        return 0

    def do_run(self, config: RunCommandConfig) -> int:
        project_slurper = YangaProjectSlurper(config.project_dir)
        if config.print:
            self.print_project_info(project_slurper)
            return 0
        if not config.variant_name:
            variant_name = prompt_user_to_select_option([variant.name for variant in project_slurper.variants])
        else:
            variant_name = config.variant_name
        if not variant_name:
            raise UserNotificationException("No variant selected. Stopping the execution.")
        if not project_slurper.pipeline:
            raise UserNotificationException("No pipeline found in the configuration.")
        # Schedule the steps to run
        steps_references = PipelineScheduler(project_slurper.pipeline, config.project_dir).get_steps_to_run(
            config.step, config.single
        )
        if not steps_references:
            if config.step:
                raise UserNotificationException(f"Step '{config.step}' not found in the pipeline.")
            self.logger.info("No steps to run.")
            return 0
        user_request = UserRequest(
            UserRequestScope.COMPONENT if config.component_name else UserRequestScope.VARIANT,
            variant_name,
            config.component_name,
            config.target,
        )
        PipelineStepsExecutor(project_slurper, variant_name, user_request, steps_references, config.force_run).run()
        return 0

    def print_project_info(self, project_slurper: YangaProjectSlurper) -> None:
        self.logger.info("-" * 80)
        self.logger.info(f"Project directory: {project_slurper.project_dir}")
        self.logger.info(f"Parsed {len(project_slurper.user_configs)} configuration file(s).")
        self.logger.info(f"Found {len(project_slurper.components_configs_pool.values())} component(s).")
        self.logger.info(f"Found {len(project_slurper.variants)} variant(s).")
        self.logger.info("Found pipeline config.")
        self.logger.info("-" * 80)

    def _register_arguments(self, parser: ArgumentParser) -> None:
        register_arguments_for_config_dataclass(parser, RunCommandConfig)