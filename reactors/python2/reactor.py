import reactors as Reactor

def main():
    """
    Exercise  utility features in Reactors base image
    """

    print("## Important Reactor attributes")
    print("UUID: {}".format(Reactor.uid))
    print("Internal nickname: {}".format(Reactor.nickname))
    print("Agave API username: {}".format(Reactor.username))

    print("## Show Reactor's filesystem paths")
    print(Reactor.storage.paths)

    print("## Reactor's context")
    print(Reactor.context)

    print("## Fetch a value from the context")
    print(Reactor.context.actor_dbid)

    print("## Show the Reactor's message.")
    # If you are running this locally, try setting a MSG
    # environment variable to see it propagate into the
    # Reactor container environment
    print(Reactor.context.raw_message)

    print("## Fetch a value for 'key1' from config.yml")
    print(Reactor.settings.key1)

    print("## Demo the built-in logger")
    Reactor.logger.info("Hello, world")

    print("## Get a UTC Timestamp")
    print(Reactor.utcnow())

    print("## Make an Agave call to the profiles API")
    try:
        print(Reactor.client.profiles.get())
    except Exception as e:
        Reactor.logger.warn("Error calling Agave: {}".format(e))
        pass

if __name__ == '__main__':
    main()
