#!/usr/bin/env python3

from ykman import list_all_devices, scan_devices, connect_to_device
from yubikit.core.smartcard import SmartCardConnection
from yubikit.oath import OathSession
from time import sleep
import sys
import os
import cmd


def trim(docstring):
    """Trim indentation from docstrings. From python.org"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = 999
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < 999:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


# Used to alter the output behavior
delay = float(os.environ.get("AUTHVENTURE_TYPE_DELAY", "0.01"))
no_upper = bool(os.environ.get("AUTHVENTURE_CASE", None))


def output(*values, sep=" "):
    if False:
        print(*values, sep=sep)
    else:
        value = sep.join(values)
        if not no_upper:
            value = value.upper()
        for c in value:
            sys.stdout.write(c)
            sys.stdout.flush()
            sleep(delay)
        print()


_numbers = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


def int2word(value):
    if not (0 <= value <= 9):
        raise ValueError("value must be 0-9")
    return _numbers[str(value)]


def format_oath(code):
    words = [_numbers[d] for d in code]
    split_i = 4 if len(words) == 8 else 3
    a = ", ".join(words[:split_i])
    b = ", ".join(words[split_i:])
    return f"{a.capitalize()}... {b.capitalize()}."


class Room:
    """No description."""

    def __init__(self, state):
        self._state = state

    def get_description(self):
        return trim(self.__doc__)

    def look(self, what):
        output(f"I see no {what} here.")

    def go(self, where):
        output("Go somewhere else!")


class House(Room):
    """
    You are standing inside a building, a well house for a large spring.
    """

    def __init__(self, state):
        super().__init__(state)
        self._yk_state = None
        self._serials = []

    def _refresh(self):
        devs, state = scan_devices()
        if self._yk_state != state:
            self._yk_state = state
            self._serials = [info.serial for _, info in list_all_devices()]

    def get_description(self):
        desc = super().get_description() + "\n\n"

        self._refresh()
        n_keys = len(self._serials)
        if "yubikey" in self._state:
            n_keys -= 1
        if n_keys > 1:
            desc += "There are some YubiKeys on the ground here."
        elif n_keys == 1:
            desc += "There is a YubiKey on the ground here."
        elif "yubikey" in self._state:
            desc += "You see an imprint in the dust from where a YubiKey once was."
        else:
            desc += (
                "You feel like something is missing, "
                "but you can't quite make the connection.\n"
                "You feel a bit unplugged."
            )

        return desc

    def go(self, where):
        if where in ("out", "outside", "road"):
            return Road(self._state)
        super().go(where)

    def look(self, what):
        if what in ("yubikeys", "keys", "yubikey", "key"):
            self._refresh()
            n_keys = len(self._serials)
            if n_keys == 0:
                output("There are no YubiKeys here. You feel a bit unplugged.")
            elif n_keys == 1:
                serial = self._serials[0]
                output(f"The YubiKey is marked with the number {serial}.")
            else:
                output(
                    f"There are {int2word(n_keys)} YubiKeys on the ground, "
                    "covered with strange markings."
                )
                for serial in self._serials:
                    output(f"One YubiKey is marked with the number {serial}.")
        else:
            super().look(what)

    def to_drop(self, what):
        if what in ("yubikey", "key"):
            if "yubikey" in self._state:
                del self._state["yubikey"]
                output(
                    "You take the YubiKey from your pocket, and drop it on the "
                    "ground."
                )
            else:
                output("You don't have a YubiKey to drop.")
        else:
            output("You cannot drop that.")

    def do_take(self, what):
        self._refresh()
        n_keys = len(self._serials)
        if what in ("yubikeys", "keys", "yubikey", "key"):
            if "yubikey" in self._state:
                output("You already have a YubiKey in your pocket.")
                return
            if n_keys == 0:
                output("There are no YubiKeys here. You feel a bit unplugged.")
            elif n_keys == 1:
                self._state["yubikey"] = self._serials[0]
                output("You take the YubiKey, and place it in your pocket.")
            else:
                output(f"There are {int2word(n_keys)} YubiKeys, don't be greedy.")
        else:
            try:
                serial = int(what)
                if serial in self._serials:
                    self._state["yubikey"] = serial
                    output("You take the YubiKey, and place it in your pocket.")
                else:
                    output(f"You don't see anything with the number {serial} here.")
            except ValueError:
                output("You can't take that.")


class Road(Room):
    """
    You are standing at the end of a road before a small brick building.
    Around you is a forest.
    A small stream flows out of the building and down a gully.
    To the east is a large cave.
    """

    def look(self, what):
        if what == "house":
            output("It looks like a brick building.")
        elif what == "cave":
            output("You see the entrance to the cave. A figure stands nearby.")
        else:
            super().look(what)

    def go(self, where):
        if where in ("house", "building"):
            return House(self._state)
        elif where == "cave":
            output(
                "As you approach the cave you see a knight standing guard beside the "
                "entrance."
            )
            output()

            if "yubikey" in self._state:
                output(
                    "\"It's dangerous to go alone! I can sense you have what it takes "
                    'to make it. Proceed."'
                )
                output()
                output(
                    "You walk past the knight and enter the cave. "
                    "Up ahead a large cavern opens up before you."
                )
                return Cave(self._state)
            else:
                output(
                    "\"It's dangerous to go alone! "
                    'I cannot let you pass without a YubiKey for protection."'
                )
        else:
            return super().go(where)


class Cave(Room):
    """
    You stand in the middle of a large cavern.
    Tunnels branch out from here leading in different directions.
    In the center sits a robed man.
    Seemingly oblivious to your presence, he mutters to himself, incoherently.
    """

    def go(self, where):
        if where in ("out", "outside", "road"):
            return Road(self._state)
        if where in ("tunnel", "tunnels", "deeper"):
            output("You look down a tunnel and see that it is pitch black.")
            output("Fearing being eaten by a grue, you decide to stay here.")
            return None
        if where in ("man", "center"):
            return Man(self._state)
        return super().go(where)


class Man(Room):
    """
    The robed man notices you and looks up. His eyes light up and he smiles broadly.

    "Welcome, stranger! I've been alone for so long...".

    He pauses, and in the flash of an instant his smile is replaced with a stern look.
    """

    def __init__(self, state):
        super().__init__(state)
        self._oath = OathSession(
            connect_to_device(state["yubikey"], [SmartCardConnection])[0]
        )

    def go(self, where):
        if where in ("back", "cave", "away"):
            return Cave(self._state)
        return super().go(where)

    def get_description(self):
        output(super().get_description())

        if self._oath.locked:
            output(
                trim(
                    """
                "Ah, but, I cannot share with you my secrets unless you can give me the
                password. I swore an oath!".
                His harsh demeanor drops slightly, as he looks at you with a glint of
                hope in his eyes. He looks at you expectantly as he continues:
                "You DO know the password, do you not? Tell me, what is it?".
                """
                )
            )

            password = input("\n> ")
            output()
            key = self._oath.derive_key(password)
            try:
                self._oath.validate(key)
                output(
                    "The smile returns. "
                    '"I knew it! Welcome, friend, let me share with you my secrets!".'
                )
            except Exception:
                return trim(
                    """
                    The man looks at you with great dissapointment in his eyes.
                    "No, no, no... That isn't it. Go away! Leave me be!"
                    """
                )

        creds = {k.id: k for k in self._oath.calculate_all()}

        output(
            trim(
                """
                He pulls out an old tattered scroll and unravels it.
                "Which secret shall I share?", he asks, as he extends a bony arm
                toward you, beckoning you to read.
                """
            )
        )
        output()

        if not creds:
            return trim(
                """
                You look at the scroll, but it is empty. The man notices your
                confusion, and looks at the blank page himself.

                "I... I don't understand. There are no secrets here. Surely you
                must have secrets to keep?!?".

                The man is noticably upset, and you deem it wise to not disturb
                him further.
                """
            )
        else:
            for cred_id in creds:
                print(cred_id.decode())

            selected = input("\n> ").encode()
            while selected not in creds:
                output(
                    trim(
                        """
                        "What? I don't understand you. Speak up!"
                        The man looks at you, expectantly.
                        """
                    )
                )
                selected = input("\n> ").encode()

            cred = creds[selected]
            output()
            output("Ahhh, of course! I knew you would choose that one!")
            output()

            if cred.touch_required:
                output(
                    trim(
                        """
                        In that case, there's just one more thing I must ask of you..."
                        As he speaks he reaches into his pocket, grasping for something.
                        As he pulls his hand back out you see a glimmer, something small
                        and metallic is clenched in his fist.
                        He slowly opens his hand for you to see a golden ring laying
                        across his palm.

                        "Are you ready?", he asks.
                        """
                    )
                )

                if input("\n> ").lower() in ("yes", "y"):
                    output()
                    output(
                        trim(
                            """
                            Without a word, the golden ring starts to pulse with a
                            bright green glow. You feel compelled to reach out and touch
                            it with your fingers.
                            """
                        )
                    )
                    output()

                    try:
                        code = self._oath.calculate_code(cred)
                        output(
                            trim(
                                """
                                As soon as you touch the gold ring it immediately stops
                                pulsing. The man pulls it close to his eyes, as if
                                struggling to read an inscription. Strange, you think to
                                yourself, you could have sworn there was nothing there a
                                moment ago.
                                """
                            )
                        )
                    except Exception:
                        return trim(
                            """
                        The man looks at you disapprovingly.

                        "Those who are to cowardly to act, will never amount to
                        anything.", he mutters as he puts the ring back into his pocket.
                        """
                        )
                else:
                    return "Then go away!"
            else:
                output(
                    trim(
                        """
                    The man reaches into his pocket, grasping for something.
                    As he pulls his hand back out you see a glimmer, something small
                    and metallic is clenched in his fist.
                    He slowly opens his hand for you to see a golden ring laying
                    across his palm. He holds the ring up close to his face, and
                    squints, and you realize he is reading an inscription.
                    """
                    )
                )
                code = self._oath.calculate_code(cred)

        output("The man reads the inscription out loud:")
        output()

        return format_oath(code.value)


class Adventicature(cmd.Cmd):
    prompt = "\n> "

    def __init__(self):
        super().__init__()
        self.state = {}
        self.room = Road(self.state)
        self.onecmd("look")

    def precmd(self, line):
        print()
        return line.lower()

    def emptyline(self):
        self.onecmd("look")

    def do_quit(self, arg):
        output("Are you sure you want to quit?\n")
        return input("> ").lower() in ("yes", "y", "quit")

    def do_look(self, arg):
        if not arg:
            output(self.room.get_description())
        else:
            self.room.look(arg)

    def do_inventory(self, arg):
        serial = self.state.get("yubikey", None)
        if serial:
            output(f"You have a YubiKey marked with the number {serial}.")
        else:
            output("Your pockets are empty, except for some lint.")

    def do_go(self, arg):
        room = self.room.go(arg)
        if room is not None:
            self.room = room
            self.onecmd("look")

    def default(self, line):
        words = line.split()
        do_func = getattr(self.room, f"do_{words[0]}", None)
        if do_func is not None and len(words) == 2:
            do_func(words[1])
        else:
            output("I don't understand what you mean.")

    def do_oath(self, arg):
        output(format_oath(arg))


def main():
    print(TITLE)
    game = Adventicature()
    game.cmdloop()


TITLE = r"""
     _         _   _                    _
    / \  _   _| |_| |____   _____ _ __ | |_ _   _ _ __ ___
   / _ \| | | | __| '_ \ \ / / _ \ '_ \| __| | | | '__/ _ \
  / ___ \ |_| | |_| | | \ V /  __/ | | | |_| |_| | | |  __/
 /_/   \_\__,_|\__|_| |_|\_/ \___|_| |_|\__|\__,_|_|  \___|
                                                 by Yubico
"""


if __name__ == "__main__":
    main()
