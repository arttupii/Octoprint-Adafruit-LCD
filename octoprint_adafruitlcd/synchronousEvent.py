from collections import deque

class SynchronousEvent:
    """
    An event object to use for the Event Queue

    Holds event string and payload dictionary
    """

    def __init__(self, event, payload):
        # type (str, dict) -> None
        self.__event = event
        self.__payload = payload
    
    def getEvent(self):
        # type() -> str
        return self.__event
    
    def getPayload(self):
        # type() -> dict
        return self.__payload

class SynchronousEventQueue:
    
    def __init__(self):
        self.__event_queue = deque()
    
    def empty(self):
        # type () -> bool
        """
        Check if the queue is empty
        :return: True if empty
        """
        return len(self.__event_queue) == 0
    
    def put(self, event):
        # type (SynchronousEvent) -> None
        """
        Add an event to the queue
        :param event: SynchronousEvent to add
        """
        self.__event_queue.append(event)
    
    def get(self):
        # type () -> SynchronousEvent
        """
        Peek at the next item in the queue
        :return: event, None if empty
        """
        if not self.empty():
            return self.__event_queue[0]
    
    def pop(self):
        # type () -> SynchronousEvent
        """
        Pop the next item in the queue
        :return: event, None if empty
        """
        if not self.empty():
            return self.__event_queue.popleft()