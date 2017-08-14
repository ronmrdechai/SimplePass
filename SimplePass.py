#!/usr/bin/env python3

import hashlib
import base64

import objc
from AppKit import *

class AlertFactory(object):
    """
    Creates alerts with default properties.
    """
    def __init__(self, title, icon):
        self._title = title
        self._icon = icon

    def make_alert(self, text, buttons=None, accessory_view=None):
        """
        Create a new alert.
        """
        alert = NSAlert.alloc().init()
        alert.setAlertStyle_(NSInformationalAlertStyle)
        alert.setMessageText_(self._title)
        if text is not None:
            alert.setInformativeText_(text)
        if buttons is not None:
            for b in buttons:
                alert.addButtonWithTitle_(b)
        if accessory_view is not None:
            alert.setAccessoryView_(accessory_view)
        icon = NSImage.alloc().initByReferencingFile_(self._icon)
        alert.setIcon_(icon)
        NSApp.activateIgnoringOtherApps_(True)
        return alert.runModal()

class LabelFactory(object):
    """
    Create labels with default properties.
    """
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def make_label(self, offset, text):
        """
        Create a label.
        """
        label = NSTextField.alloc().initWithFrame_(NSMakeRect(*offset, self._width, self._height))
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        label.setEditable_(False)
        label.setSelectable_(False)
        label.setStringValue_(text)
        return label

alert_factory = AlertFactory("Password manager", "/System/Library/Frameworks/SecurityInterface.framework/Versions/A/Resources/Lock_Locked State@2x.png")
label_facotry = LabelFactory(200, 24)

fields = NSCollectionView.alloc().initWithFrame_(NSMakeRect(0, 0, 315, 84))
fields.setBackgroundColors_([NSColor.clearColor()])

fields.addSubview_(label_facotry.make_label((0, 3), "Master password:"))
master_password = NSSecureTextField.alloc().initWithFrame_(NSMakeRect(115, 0, 200, 24))
master_password.setStringValue_("")
fields.addSubview_(master_password)

fields.addSubview_(label_facotry.make_label((0, 33), "Domain:"))
domain = NSTextField.alloc().initWithFrame_(NSMakeRect(115, 30, 200, 24))
domain.setStringValue_("example.com")
fields.addSubview_(domain)

fields.addSubview_(label_facotry.make_label((0, 63), "Password number:"))
number = NSTextField.alloc().initWithFrame_(NSMakeRect(115, 60, 200, 24))
number.setStringValue_("0")
fields.addSubview_(number)

if alert_factory.make_alert("Enter password properties", accessory_view=fields) \
        == NSAlertAlternateReturn:
    master_password.validateEditing()
    master_password = master_password.stringValue()

    domain.validateEditing()
    domain = domain.stringValue()

    number.validateEditing()
    number = number.stringValue()

    password = base64.b64encode(hashlib.pbkdf2_hmac(
        'sha256',
        (master_password + '/' + domain).encode(),
        b'',
        100000 + int(number)
    )).decode()[0:16] + 'Aa$1'

    pasteboard = NSPasteboard.generalPasteboard()
    pasteboard.declareTypes_owner_(NSArray.arrayWithObjects_(NSStringPboardType, None), None)
    pasteboard.setString_forType_(password, NSStringPboardType)
    if alert_factory.make_alert("Password copied to clipboard!", ["OK", "Show password"]) \
            == NSAlertSecondButtonReturn:
        alert_factory.make_alert("Generated password '%s'" % password)
