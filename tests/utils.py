from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config

from itmo_ai_timetable.settings import Settings

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(cmd_opts: SimpleNamespace, base_path: Path = PROJECT_PATH) -> Config:
    database_uri = Settings().database_uri

    path_to_folder = PROJECT_PATH  #  cmd_opts.config
    # Change path to alembic.ini to absolute
    # if not os.path.isabs(cmd_opts.config):
    #     cmd_opts.config = os.path.join(base_path,"alembic.ini" ) # cmd_opts.config + "alembic.ini"
    cmd_opts.config = base_path / "alembic.ini"

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)
    config.attributes["configure_logger"] = False

    # Change path to alembic folder to absolute
    migrations_location = Path(config.get_main_option("script_location"))
    if not migrations_location.is_absolute():
        config.set_main_option("script_location", str(base_path / path_to_folder / migrations_location))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", database_uri)

    return config
