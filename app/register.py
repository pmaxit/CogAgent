"""
This file registers all meta-operations that CogAgent1.5-9B Model can perform,
along with the required keywords that must be included for each meta-operation.

key: value
meta-operation: keyword
"""

import pyautogui
import pyperclip
import time
import os
import platform

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1

# TODO: Support other META_PARAMETER and other META_OPERATION
META_PARAMETER = {
    # Meta-operations need to contain keywords
    "CLICK": ["box"],
    "DOUBLE_CLICK": ["box"],
    "RIGHT_CLICK": ["box"],
    "TYPE": ["box", "text"],
    "HOVER": ["box"],
    "SCROLL_DOWN": ["box"],
    "SCROLL_UP": ["box"],
    # "SCROLL_RIGHT": ["box"],
    # "SCROLL_LEFT": ["box"],
    "KEY_PRESS": ["key"],
    "LAUNCH": ["app"],
    # "QUOTE_TEXT": ["box"],
    # "QUOTE_CLIPBOARD": ["output"],
    # "TEXT_FORMAT": ["input"],
    # "LLM": ["prompt"],
    "END": [""],
}


def identify_os():
    os_detail = platform.platform()
    if "mac" in os_detail.lower() or "darwin" in os_detail.lower():
        return "Mac"
    elif "windows" in os_detail.lower():
        return "Win"
    elif "linux" in os_detail.lower():
        return "Linux"
    else:
        raise ValueError(
            f"This {os_detail} operating system is not currently supported!"
        )


def paste(text):
    pyperclip.copy(text)
    time.sleep(1)
    os_type = identify_os()
    if os_type == "Mac":
        with pyautogui.hold("command"):
            pyautogui.press("v")
    elif os_type == "Win" or os_type == "Linux":
        with pyautogui.hold("ctrl"):
            pyautogui.press("v")


def click(params):
    """
    Meta-operation: CLICK
    CLICK: Simulate a left-click at the center position of the box.
    """
    pyautogui.click(params["box"])


def double_click(params):
    """
    Meta-operation: DOUBLE_CLICK
    DOUBLE_CLICK: Simulate a double-click the center position of the box.
    """
    pyautogui.doubleClick(params["box"])


def right_click(params):
    """
    Meta-operation: RIGHT_CLICK
    RIGHT_CLICK: Simulate a right-click at the center position of the box.
    """
    pyautogui.rightClick(params["box"])


def type_input(params):
    """
    Meta-operation: TYPE
    TYPE: At the center position of the box, simulate keyboard input to enter text.
    """
    paste(params["text"])
    pyautogui.press("Return")


def hover(params):
    """
    Meta-operation: HOVER
    HOVER: Move the mouse to the center position of the box.
    """
    pyautogui.moveTo(params["box"])


def scroll_down(params):
    """
    Meta-operation: SCROLL_DOWN
    SCROLL_DOWN: Move the mouse to the center position of the box, then scroll the screen downward.
    """
    pyautogui.moveTo(params["box"])
    pyautogui.scroll(-10)


def scroll_up(params):
    """
    Meta-operation: SCROLL_UP
    SCROLL_UP: Move the mouse to the center position of the box, then scroll the screen up.
    """
    pyautogui.moveTo(params["box"])
    pyautogui.scroll(10)


def key_press(params):
    """
    Meta-operation: KEY_PRESS
    TYPE: Press a special key on the keyboard. eg: KEY_PRESS(key='Return').
    """
    pyautogui.press(params["key"])


def end(params):
    print("Workflow Completed!")


def launch(params):
    os_type = identify_os()
    app_name = params["app"][1:-1] if len(params["app"]) > 2 else params["app"]
    
    if os_type == "Mac":
        system_app_dir = "/System/Applications"
        applications_dir = "/Applications"
        if os.path.exists(applications_dir):
            applications = [app for app in os.listdir(applications_dir) if app.endswith(".app")]
        else:
            applications = []
        if os.path.exists(system_app_dir):
            system_apps = [app for app in os.listdir(system_app_dir) if app.endswith(".app")]
        else:
            system_apps = []
        all_apps = applications + system_apps
        for app in all_apps:
            if app_name in app:
                app_dir = applications_dir + "/" + app if app in applications else system_app_dir + "/" + app
                os.system(f"open -a '{app_dir}'")
                break
    elif os_type == "Linux":
        # Try common Linux application launch methods
        # First try to launch directly
        if os.system(f"which {app_name.lower()} > /dev/null 2>&1") == 0:
            os.system(f"{app_name.lower()} &")
        # Try with xdg-open for desktop files
        elif os.path.exists(f"/usr/share/applications/{app_name.lower()}.desktop"):
            os.system(f"xdg-open /usr/share/applications/{app_name.lower()}.desktop &")
        # Try gtk-launch
        else:
            os.system(f"gtk-launch {app_name.lower()} 2>/dev/null || xdg-open {app_name.lower()} 2>/dev/null &")
    elif os_type == "Win":
        # Windows application launch
        os.system(f"start {app_name}")

META_OPERATION = {
    # Defining meta-operation functions
    "CLICK": click,
    "DOUBLE_CLICK": double_click,
    "RIGHT_CLICK": right_click,
    "TYPE": type_input,
    "HOVER": hover,
    "SCROLL_DOWN": scroll_down,
    "SCROLL_UP": scroll_up,
    # "SCROLL_RIGHT": ["box"], 
    # "SCROLL_LEFT": ["box"],
    "KEY_PRESS": key_press,
    "LAUNCH": launch,
    # "QUOTE_TEXT": ["box"],
    # "QUOTE_CLIPBOARD": ["output"],
    # "TEXT_FORMAT": ["input"],
    # "LLM": ["prompt"],
    "END": end,
}


def locateOnScreen(image, screenshotIm):
    print(image, screenshotIm)
    start = time.time()
    while True:
        try:
            # the locateAll() function must handle cropping to return accurate coordinates,
            # so don't pass a region here.
            retVal = pyautogui.locate(image, screenshotIm)
            try:
                screenshotIm.fp.close()
            except AttributeError:
                # Screenshots on Windows won't have an fp since they came from
                # ImageGrab, not a file. Screenshots on Linux will have fp set
                # to None since the file has been unlinked
                pass
            if retVal or time.time() - start > 0:
                return retVal
        except:
            if time.time() - start > 0:
                return None


def convert_to_meta_operation(Grounded_Operation):
    detailed_operation = {}
    if Grounded_Operation["operation"] in META_PARAMETER:
        detailed_operation["meta"] = Grounded_Operation["operation"]
        for value in META_PARAMETER[Grounded_Operation["operation"]]:
            if value in Grounded_Operation:
                # Note: Screenshot captures only left half of screen, so x coordinates are adjusted accordingly
                if value == "box":
                    # number = (left, top, width, height)
                    numbers = Grounded_Operation["box"]
                    box = [num / 1000 for num in numbers]
                    # box = (left/1000, top/1000, width/1000, height/1000)
                    screen_width, screen_height = pyautogui.size()
                    # Since screenshot is only left half of screen, adjust x coordinates
                    # x coordinates in screenshot are relative to left half (0 to 0.5 of full screen)
                    # y coordinates remain the same (0 to 1 of full screen)
                    x_min, y_min, x_max, y_max = [
                        int(coord * screen_width // 2) if i % 2 == 0 else int(coord * screen_height)
                        for i, coord in enumerate(box)
                    ]
                    x, y = (x_min + x_max) / 2, (y_min + y_max) / 2
                    detailed_operation[value] = (x, y)
                else:
                    detailed_operation[value] = Grounded_Operation[value][1:-1]
        print(detailed_operation)
        return detailed_operation
    else:
        raise "Wrong operation or operation not registered!"


def agent(Grounded_Operation):
    detailed_operation = convert_to_meta_operation(Grounded_Operation)
    META_OPERATION[detailed_operation["meta"]](detailed_operation)
    time.sleep(2)
    return detailed_operation["meta"]
