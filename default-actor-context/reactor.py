import os
import sys
import pdb
import traceback
from reactors.runtime import Reactor
from reactors.version import version as reactors_version


def main():
    r = Reactor()

    # validate the message and context against schemas
    try:
        r.validate_message(permissive=False)
    except Exception as err:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
        raise

    r.logger.info("Actor received message: {}".format(r.context['raw_message']))
    r.logger.debug("This is a DEBUG message from actor {}".format(r.uid))
    r.logger.info("This is an INFO message from actor {}".format(r.uid))
    r.logger.warning("This is a warning from actor {}".format(r.uid))
    r.logger.info("Here's that secret value: {}".format(r.context.get('dont_reveal')))
    r.logger.info("Here's that value from the config.yml: {}".format(
        r.settings.do_reveal))
    r.logger.info(f"Using python-reactors version {reactors_version}")

    # check filesystem availability
    paths = ['/work/projects']
    avail = {p: os.path.exists(p) for p in paths}
    if all(avail.values()):
        [r.logger.debug(f"path '{p}' exists") for p in avail]
        r.on_success(f"all checked paths exist")
    else:
        unavail = [p for p in avail if not avail[p]]
        r.logger.error(f"The following paths do not exist: {unavail}")


if __name__ == '__main__':
    main()
