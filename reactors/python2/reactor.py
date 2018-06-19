from reactors.runtime import Reactor, utcnow, agaveutils


def main():
    """
    Exercise  utility features in Reactors base image
    """
    r = Reactor()

    r.logger.info("# Reactor attributes")

    r.logger.info("UUID: {}".format(r.uid))
    r.logger.info("Reactor logging nickname: {}".format(r.nickname))
    r.logger.info("API username: {}".format(r.username))

    # r.logger.info("# Reactor filesystem paths")
    # r.logger.info(r.storage.paths)

    r.logger.info("# Reactor context")
    r.logger.info(r.context)

    r.logger.info("# Actor database id")
    r.logger.info(r.context.actor_dbid)

    r.logger.info("# Reactor message")
    # If you are running this locally, try setting a MSG
    # environment variable to see it propagate into the
    # Reactor container environment
    r.logger.info(r.context.raw_message)

    r.logger.info("# Value of 'key1' from settings")
    r.logger.info(r.settings.key1)

    r.logger.info("# Demonstrate logger")
    r.logger.info("Hello, world")

    r.logger.info("# UTC Timestamp")
    r.logger.info(utcnow())

    r.logger.info("# Call Agave profiles API")
    try:
        r.logger.info(r.client.profiles.get())
    except Exception as e:
        r.logger.error("Error calling API: {}".format(e))
        pass

    print(agaveutils.uri.to_agave_uri('data-sd2e-community', '/sample'))


if __name__ == '__main__':
    main()
