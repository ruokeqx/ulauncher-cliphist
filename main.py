from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

import subprocess
from fuzzywuzzy import process, fuzz


class CliphistExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or str()
        p = subprocess.Popen('cliphist list',shell=True,stdout=subprocess.PIPE)
        clipdb,_ = p.communicate()
        clipdb = clipdb.decode().split('\n')
        items = []
        clip_matches = process.extract(query, choices=clipdb, limit=20, scorer=fuzz.partial_ratio)
        for clip in clip_matches:
            res = subprocess.Popen(["cliphist","decode"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
            res.stdin.write(clip[0].encode())
            res.stdin.close()
            res.wait()
            res = res.stdout.read()
            items.append(ExtensionResultItem(icon='images/cliphist.svg',
                                             name='%s' % clip[0],
                                             on_enter=CopyToClipboardAction(res.decode())))
        return RenderResultListAction(items)


if __name__ == '__main__':
    CliphistExtension().run()
