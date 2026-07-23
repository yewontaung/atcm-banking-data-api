from app.utils.managers.event import SimpleEventManager


event_manager = SimpleEventManager()

listen = event_manager.listen

publish = event_manager.publish