#!/usr/bin/env python3
import time

from dbus import service

from notification import Notification


class NotificationHandler(service.Object):

    def __init__(self, conn, object_path, queue):
        super().__init__(conn, object_path)
        self.nq = queue

    def create_activate_callback(self, actions):
        if "default" in actions:
            return lambda nid: self.ActionInvoked(nid, "default")
        else:
            return lambda nid: None

    @service.method("org.freedesktop.Notifications",
                    in_signature='susssasa{ss}i',
                    out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon,
               summary, body, actions, hints, expire_timeout):
        notification = Notification()
        notification.id = replaces_id
        notification.application = str(app_name)
        notification.summary = str(summary)
        notification.body = str(body)
        notification.activate_callback = self.create_activate_callback(actions)
        if int(expire_timeout) > 0:
            notification.deadline = time.time() + int(expire_timeout) / 1000.0
        if 'urgency' in hints:
            notification.urgency = int(hints['urgency'])
        self.nq.put(notification)
        return notification.id

    @service.signal("org.freedesktop.Notifications", signature='us')
    def ActionInvoked(self, id_in, action_key_in):
        pass

    @service.method("org.freedesktop.Notifications", in_signature='', out_signature='as')
    def GetCapabilities(self):
        return ("actions", "body")

    @service.method("org.freedesktop.Notifications", in_signature='u', out_signature='')
    def CloseNotification(self, id):
        self.nq.remove(id)

    @service.signal('org.freedesktop.Notifications', signature='uu')
    def NotificationClosed(self, id_in, reason_in):
        pass

    @service.method("org.freedesktop.Notifications", in_signature='', out_signature='ssss')
    def GetServerInformation(self):
        return ("rofication", "http://gmpclient.org/", "0.0.1", "1")
