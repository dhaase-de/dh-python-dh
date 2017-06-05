#!/usr/bin/python3

import dh.utils


###
#%% main
###


class Matter():
    states = ["solid", "liquid", "gas", "plasma"]

    def __init__(self):
        self.fsm = dh.utils.Fsm(model=self, states=Foo.states, initial="solid")
        self.fsm.add_transition("melt", "solid", "liquid")
        self.fsm.add_transition("evaporate", "liquid", "gas", before=self.before_evaporate)
        self.fsm.on_enter_liquid(self.entering_liquid)

    def before_evaporate(self):
        """
        Triggered by transition "evaporate: liquid -> gas".
        """
        print("About to evaporate...")

    def entering_liquid(self):
        """
        Triggered by entering state "liquid".
        """
        print("Becoming liquid...")


def main():
    matter = Matter()
    print(matter.state)
    matter.melt()
    print(matter.state)
    matter.evaporate()
    print(matter.state)


if __name__ == "__main__":
    main()

