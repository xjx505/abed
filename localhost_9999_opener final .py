"""Wrapper that restores the original localhost_9999 opener from cached bytecode."""

from __future__ import annotations

import marshal
import os
import random
from pathlib import Path
import time

WRAPPER_PATH = Path(__file__).resolve()
PYC_PATH = WRAPPER_PATH.parent / "__pycache__" / "localhost_9999_opener (1) (1).cpython-314.pyc"
PYC_HEADER_SIZE = 16
CHORD_WINDOW_SECONDS = 0.30
ROBUST_POLL_INTERVAL_SECONDS = 0.005
HOVER_ANCHOR_POLL_INTERVAL_SECONDS = 0.05
WS_EX_NOACTIVATE = 0x08000000
MK_SHIFT_FALLBACK = 0x0004
MK_CONTROL_FALLBACK = 0x0008
VK_MENU_CODE = 0x12          # Alt key (left or right)
OPACITY_ZERO = 0             # completely hidden
TRIPLE_ESCAPE_WINDOW = 1.5   # seconds for triple-Escape


def patch_recovered_module(module_globals: dict[str, object]) -> None:
    """Improve hotkey reliability and mirror browser input without stealing mouse ownership."""
    module_globals["HOTKEY_POLL_INTERVAL_SECONDS"] = min(
        float(module_globals.get("HOTKEY_POLL_INTERVAL_SECONDS", ROBUST_POLL_INTERVAL_SECONDS)),
        ROBUST_POLL_INTERVAL_SECONDS,
    )
    module_globals["privacy_input_mode"] = False
    module_globals["dim_mode"] = False

    ctypes_module = module_globals["ctypes"]
    user32 = module_globals["user32"]
    threading_module = module_globals["threading"]
    hotkey_poll_stop = module_globals["hotkey_poll_stop"]
    capslock_poll_stop = module_globals["capslock_poll_stop"]
    try_trigger_hotkey = module_globals["try_trigger_hotkey"]
    try_trigger_screenshot = module_globals["try_trigger_screenshot"]
    try_trigger_active_window_screenshot_and_open = module_globals["try_trigger_active_window_screenshot_and_open"]
    reset_hotkey_state = module_globals["reset_hotkey_state"]
    request_shutdown = module_globals["request_shutdown"]
    set_window_opacity = module_globals["set_window_opacity"]
    set_click_through = module_globals["set_click_through"]
    show_browser_topmost_no_focus = module_globals["show_browser_topmost_no_focus"]
    is_capslock_on = module_globals["is_capslock_on"]
    is_window_alive = module_globals["is_window_alive"]
    forward_keyboard_to_browser = module_globals["forward_keyboard_to_browser"]
    logger = module_globals["logger"]
    hookproc_type = module_globals["HOOKPROC"]
    point_type = module_globals["POINT"]
    kbd_struct = module_globals["KBDLLHOOKSTRUCT"]
    mouse_struct = module_globals["MSLLHOOKSTRUCT"]
    hc_action = module_globals["HC_ACTION"]
    wh_keyboard_ll = module_globals["WH_KEYBOARD_LL"]
    wh_mouse_ll = module_globals["WH_MOUSE_LL"]
    wm_keydown = module_globals["WM_KEYDOWN"]
    wm_keyup = module_globals["WM_KEYUP"]
    wm_syskeydown = module_globals["WM_SYSKEYDOWN"]
    wm_syskeyup = module_globals["WM_SYSKEYUP"]
    wm_mousemove = module_globals["WM_MOUSEMOVE"]
    wm_mousewheel = module_globals["WM_MOUSEWHEEL"]
    wm_lbuttondown = module_globals["WM_LBUTTONDOWN"]
    wm_lbuttonup = module_globals["WM_LBUTTONUP"]
    wm_rbuttondown = module_globals["WM_RBUTTONDOWN"]
    wm_rbuttonup = module_globals["WM_RBUTTONUP"]
    wm_mbuttondown = module_globals["WM_MBUTTONDOWN"]
    wm_mbuttonup = module_globals["WM_MBUTTONUP"]
    mk_lbutton = module_globals.get("MK_LBUTTON", 0x0001)
    mk_rbutton = module_globals.get("MK_RBUTTON", 0x0002)
    mk_shift = module_globals.get("MK_SHIFT", MK_SHIFT_FALLBACK)
    mk_control = module_globals.get("MK_CONTROL", MK_CONTROL_FALLBACK)
    mk_mbutton = module_globals.get("MK_MBUTTON", 0x0010)
    vk_escape = module_globals["VK_ESCAPE"] if "VK_ESCAPE" in module_globals else 0x1B
    vk_lcontrol = module_globals["VK_LCONTROL"]
    vk_rcontrol = module_globals["VK_RCONTROL"]
    vk_lshift = module_globals["VK_LSHIFT"]
    vk_rshift = module_globals["VK_RSHIFT"]
    vk_lwin = module_globals["VK_LWIN"]
    vk_rwin = module_globals["VK_RWIN"]
    vk_a = module_globals["VK_A"]
    vk_s = module_globals["VK_S"]
    vk_capital = module_globals["VK_CAPITAL"]
    browser_opacity_active = module_globals["BROWSER_OPACITY_ACTIVE"]
    browser_opacity_inactive = module_globals["BROWSER_OPACITY_INACTIVE"]
    capslock_poll_interval = module_globals["CAPSLOCK_POLL_INTERVAL_SECONDS"]
    hwnd_value = module_globals["hwnd_value"]
    screen_to_client_lparam = module_globals["screen_to_client_lparam"]
    gwl_exstyle = module_globals["GWL_EXSTYLE"]
    user32.WindowFromPoint.argtypes = [point_type]
    user32.WindowFromPoint.restype = ctypes_module.c_void_p

    # ── Private clipboard setup ───────────────────────────────────────────────
    kernel32 = module_globals["kernel32"]
    _vk_c   = 0x43   # VK_C
    _vk_v   = 0x56   # VK_V
    _CF_UNICODE      = 13
    _KF_KEYUP        = 0x0002
    _KF_SCANCODE     = 0x0008
    _KF_UNICODE      = 0x0004
    _MAPVK_VK_TO_VSC = 0
    _SCAN_LSHIFT     = 0x2A
    _INPUT_KB        = 1

    # Set correct return types so 64-bit handles aren't truncated
    user32.OpenClipboard.argtypes  = [ctypes_module.c_void_p]
    user32.OpenClipboard.restype   = ctypes_module.c_bool
    user32.GetClipboardData.argtypes = [ctypes_module.c_uint]
    user32.GetClipboardData.restype  = ctypes_module.c_void_p
    user32.EmptyClipboard.restype  = ctypes_module.c_bool
    user32.CloseClipboard.restype  = ctypes_module.c_bool
    kernel32.GlobalLock.argtypes   = [ctypes_module.c_void_p]
    kernel32.GlobalLock.restype    = ctypes_module.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes_module.c_void_p]
    kernel32.GlobalUnlock.restype  = ctypes_module.c_bool
    user32.VkKeyScanW.argtypes     = [ctypes_module.c_wchar]
    user32.VkKeyScanW.restype      = ctypes_module.c_short   # signed — -1 = not found
    user32.MapVirtualKeyW.argtypes = [ctypes_module.c_uint, ctypes_module.c_uint]
    user32.MapVirtualKeyW.restype  = ctypes_module.c_uint
    user32.SendInput.argtypes      = [ctypes_module.c_uint, ctypes_module.c_void_p, ctypes_module.c_int]
    user32.SendInput.restype       = ctypes_module.c_uint

    # SendInput structures
    _ptr_size = ctypes_module.sizeof(ctypes_module.c_void_p)
    _ULONG_PTR = ctypes_module.c_uint64 if _ptr_size == 8 else ctypes_module.c_ulong

    class _KEYBDINPUT(ctypes_module.Structure):
        _fields_ = [
            ("wVk",         ctypes_module.c_ushort),
            ("wScan",       ctypes_module.c_ushort),
            ("dwFlags",     ctypes_module.c_ulong),
            ("time",        ctypes_module.c_ulong),
            ("dwExtraInfo", _ULONG_PTR),
        ]

    class _MOUSEINPUT(ctypes_module.Structure):
        # Included so the union is sized correctly (MOUSEINPUT > KEYBDINPUT).
        _fields_ = [
            ("dx",          ctypes_module.c_long),
            ("dy",          ctypes_module.c_long),
            ("mouseData",   ctypes_module.c_ulong),
            ("dwFlags",     ctypes_module.c_ulong),
            ("time",        ctypes_module.c_ulong),
            ("dwExtraInfo", _ULONG_PTR),
        ]

    class _INPUT_UNION(ctypes_module.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]

    class _INPUT(ctypes_module.Structure):
        _fields_ = [("type", ctypes_module.c_ulong), ("_u", _INPUT_UNION)]

    module_globals["_stored"] = ""   # private clipboard — never touches the OS clipboard

    def _clip_read() -> str:
        if not user32.OpenClipboard(0):
            return ""
        try:
            handle = user32.GetClipboardData(_CF_UNICODE)
            if not handle:
                return ""
            ptr = kernel32.GlobalLock(handle)
            if not ptr:
                return ""
            try:
                return ctypes_module.wstring_at(ptr)
            finally:
                kernel32.GlobalUnlock(handle)
        except Exception:
            return ""
        finally:
            user32.CloseClipboard()

    def _clip_wipe() -> None:
        if user32.OpenClipboard(0):
            user32.EmptyClipboard()
            user32.CloseClipboard()

    def _snap_clipboard() -> None:
        """Background thread: wait for the app to copy, snag it, wipe the OS clipboard."""
        time.sleep(0.08)
        text = _clip_read()
        if text:
            module_globals["_stored"] = text
            _clip_wipe()
            logger.info("Private clip: captured %d chars, OS clipboard wiped.", len(text))
        else:
            logger.info("Private clip: clipboard empty after Ctrl+C.")

    def _ki(scan_or_char: int, flags: int) -> _INPUT:
        inp = _INPUT()
        inp.type              = _INPUT_KB
        inp._u.ki.wVk         = 0
        inp._u.ki.wScan       = scan_or_char
        inp._u.ki.dwFlags     = flags
        inp._u.ki.time        = 0
        inp._u.ki.dwExtraInfo = 0
        return inp

    def _send(*inputs: _INPUT) -> None:
        arr = (_INPUT * len(inputs))(*inputs)
        user32.SendInput(len(inputs), arr, ctypes_module.sizeof(_INPUT))

    def _type_unicode_char(char: str) -> None:
        c = ord(char)
        _send(_ki(c, _KF_UNICODE))
        time.sleep(random.uniform(0.01, 0.04))
        _send(_ki(c, _KF_UNICODE | _KF_KEYUP))

    def type_stored_content() -> None:
        """Inject _stored character-by-character via scan codes — bypasses paste blocks."""
        text = str(module_globals.get("_stored", ""))
        for char in text:
            vk_full = user32.VkKeyScanW(char)
            if vk_full == -1:
                _type_unicode_char(char)
            else:
                vk        = vk_full & 0xFF
                modifiers = (vk_full >> 8) & 0xFF
                shift     = bool(modifiers & 0x01)
                if modifiers & ~0x01:          # Ctrl/Alt combos → Unicode fallback
                    _type_unicode_char(char)
                    continue
                scan = user32.MapVirtualKeyW(vk, _MAPVK_VK_TO_VSC)
                if not scan:
                    _type_unicode_char(char)
                    continue
                downs = []
                if shift:
                    downs.append(_ki(_SCAN_LSHIFT, _KF_SCANCODE))
                downs.append(_ki(scan, _KF_SCANCODE))
                _send(*downs)
                time.sleep(random.uniform(0.01, 0.04))
                ups = [_ki(scan, _KF_SCANCODE | _KF_KEYUP)]
                if shift:
                    ups.append(_ki(_SCAN_LSHIFT, _KF_SCANCODE | _KF_KEYUP))
                _send(*ups)
            time.sleep(random.uniform(0.01, 0.04))

    def set_noactivate(hwnd: int, enabled: bool) -> None:
        ex_style = user32.GetWindowLongW(hwnd, gwl_exstyle)
        if enabled:
            user32.SetWindowLongW(hwnd, gwl_exstyle, ex_style | WS_EX_NOACTIVATE)
        else:
            user32.SetWindowLongW(hwnd, gwl_exstyle, ex_style & ~WS_EX_NOACTIVATE)

    def capture_hover_anchor() -> None:
        point = point_type()
        if not user32.GetCursorPos(ctypes_module.byref(point)):
            module_globals["privacy_anchor_hwnd"] = 0
            return

        anchor_hwnd = hwnd_value(user32.WindowFromPoint(point))
        module_globals["privacy_anchor_hwnd"] = anchor_hwnd
        module_globals["privacy_anchor_x"] = point.x
        module_globals["privacy_anchor_y"] = point.y

    def ensure_hover_anchor_thread() -> None:
        existing = module_globals.get("hover_anchor_thread")
        if existing and existing.is_alive():
            return

        def poller() -> None:
            while not capslock_poll_stop.is_set():
                if module_globals.get("privacy_input_mode"):
                    anchor_hwnd = module_globals.get("privacy_anchor_hwnd") or 0
                    if anchor_hwnd:
                        lparam = screen_to_client_lparam(
                            anchor_hwnd,
                            int(module_globals.get("privacy_anchor_x", 0)),
                            int(module_globals.get("privacy_anchor_y", 0)),
                        )
                        user32.PostMessageW(anchor_hwnd, module_globals["WM_MOUSEMOVE"], 0, lparam)
                time.sleep(HOVER_ANCHOR_POLL_INTERVAL_SECONDS)

        thread = threading_module.Thread(target=poller, daemon=True)
        module_globals["hover_anchor_thread"] = thread
        thread.start()
        logger.info("Underlying hover anchor thread started.")

    def browser_privacy_active() -> bool:
        hwnd = module_globals.get("last_browser_hwnd")
        return bool(
            module_globals.get("privacy_input_mode")
            and hwnd
            and is_window_alive(hwnd)
        )

    def forward_mouse_message_to_browser(
        msg_type: int,
        screen_x: int,
        screen_y: int,
        mouse_data: int,
        state: dict[str, object],
    ) -> None:
        hwnd = module_globals.get("last_browser_hwnd")
        if not hwnd:
            return

        wparam = 0
        if state["shift_down"]:
            wparam |= mk_shift
        if state["ctrl_down"]:
            wparam |= mk_control
        if state["mouse_left_down"]:
            wparam |= mk_lbutton
        if state["mouse_right_down"]:
            wparam |= mk_rbutton
        if state["mouse_middle_down"]:
            wparam |= mk_mbutton

        if msg_type == wm_mousewheel:
            delta = ctypes_module.c_short((mouse_data >> 16) & 0xFFFF).value
            wparam |= (delta & 0xFFFF) << 16

        lparam = screen_to_client_lparam(hwnd, screen_x, screen_y)
        user32.PostMessageW(hwnd, msg_type, wparam, lparam)

    def start_hotkey_poll_thread() -> None:
        hotkey_poll_stop.clear()

        def poller() -> None:
            prev_ctrl_pressed = False
            prev_shift_pressed = False
            last_ctrl_press = 0.0
            last_shift_press = 0.0

            while not hotkey_poll_stop.is_set():
                now = time.monotonic()
                ctrl_pressed = bool(
                    (user32.GetAsyncKeyState(vk_lcontrol) & 0x8000)
                    or (user32.GetAsyncKeyState(vk_rcontrol) & 0x8000)
                )
                shift_pressed = bool(
                    (user32.GetAsyncKeyState(vk_lshift) & 0x8000)
                    or (user32.GetAsyncKeyState(vk_rshift) & 0x8000)
                )

                if ctrl_pressed and not prev_ctrl_pressed:
                    last_ctrl_press = now
                if shift_pressed and not prev_shift_pressed:
                    last_shift_press = now

                within_chord_window = (
                    abs(last_ctrl_press - last_shift_press) <= CHORD_WINDOW_SECONDS
                    and (ctrl_pressed or shift_pressed)
                )

                if (ctrl_pressed and shift_pressed) or within_chord_window:
                    try_trigger_hotkey("ctrl+shift-robust-poll")
                else:
                    reset_hotkey_state()

                prev_ctrl_pressed = ctrl_pressed
                prev_shift_pressed = shift_pressed
                time.sleep(ROBUST_POLL_INTERVAL_SECONDS)

        thread = threading_module.Thread(target=poller, daemon=True)
        module_globals["hotkey_poll_thread"] = thread
        thread.start()
        logger.info(
            "Robust Ctrl+Shift polling fallback started (window=%ss, interval=%ss).",
            CHORD_WINDOW_SECONDS,
            ROBUST_POLL_INTERVAL_SECONDS,
        )

    def start_capslock_poll_thread() -> None:
        capslock_poll_stop.clear()
        # Detect whether the opacity API uses float (0.0-1.0) or int (0-255) scale.
        if isinstance(browser_opacity_active, float):
            _full, _half, _zero = 1.0, 0.5, 0.0
        else:
            _full, _half, _zero = 255, 128, 0

        def poller() -> None:
            caps_was_held = False
            caps_press_time = 0.0
            browser_shown = False
            last_dim = None

            while not capslock_poll_stop.is_set():
                hwnd = module_globals.get("last_browser_hwnd")
                if not hwnd or not is_window_alive(hwnd):
                    time.sleep(ROBUST_POLL_INTERVAL_SECONDS)
                    continue

                caps_held = bool(user32.GetAsyncKeyState(vk_capital) & 0x8000)
                dim = bool(module_globals.get("dim_mode", False))
                now = time.monotonic()

                if caps_held and not caps_was_held:
                    caps_press_time = now

                if not caps_held:
                    if browser_shown:
                        module_globals["privacy_input_mode"] = False
                        module_globals["browser_has_focus"] = False
                        set_window_opacity(hwnd, _zero)
                        browser_shown = False
                    caps_press_time = 0.0
                elif now - caps_press_time >= 0.5:
                    if not browser_shown or dim != last_dim:
                        module_globals["privacy_input_mode"] = True
                        module_globals["browser_has_focus"] = False
                        set_window_opacity(hwnd, _half if dim else _full)
                        set_click_through(hwnd, True)
                        set_noactivate(hwnd, True)
                        show_browser_topmost_no_focus(hwnd)
                        browser_shown = True

                caps_was_held = caps_held
                last_dim = dim
                time.sleep(ROBUST_POLL_INTERVAL_SECONDS)

        thread = threading_module.Thread(target=poller, daemon=True)
        module_globals["capslock_poll_thread"] = thread
        thread.start()
        logger.info("CapsLock-hold-visibility + Alt-dim polling started.")

    def install_keyboard_hook() -> None:
        state = {
            "ctrl_down": False,
            "shift_down": False,
            "win_down": False,
            "s_down": False,
            "a_down": False,
            "capslock_key_down": False,
            "escape_down": False,
            "escape_t1": 0.0,
            "escape_t2": 0.0,
            "alt_tap_start": 0.0,
            "alt_down": False,
            "last_mouse_forward_log_time": 0.0,
            "mouse_left_down": False,
            "mouse_right_down": False,
            "mouse_middle_down": False,
        }

        def keyboard_proc(n_code: int, w_param: int, l_param: int) -> int:
            if n_code == hc_action:
                key_info = ctypes_module.cast(l_param, ctypes_module.POINTER(kbd_struct)).contents
                vk_code = key_info.vkCode
                scan_code = key_info.scanCode
                key_down = w_param in (wm_keydown, wm_syskeydown)
                key_up = w_param in (wm_keyup, wm_syskeyup)

                if vk_code in (vk_lcontrol, vk_rcontrol):
                    state["ctrl_down"] = key_down if key_down else (not key_up and state["ctrl_down"])
                if vk_code in (vk_lshift, vk_rshift):
                    state["shift_down"] = key_down if key_down else (not key_up and state["shift_down"])
                if vk_code in (vk_lwin, vk_rwin):
                    state["win_down"] = key_down if key_down else (not key_up and state["win_down"])
                if vk_code == vk_s:
                    state["s_down"] = key_down if key_down else (not key_up and state["s_down"])
                if vk_code == vk_a:
                    state["a_down"] = key_down if key_down else (not key_up and state["a_down"])
                if vk_code == vk_capital:
                    state["capslock_key_down"] = key_down if key_down else (not key_up and state["capslock_key_down"])

                if vk_code == vk_escape:
                    if key_down and not state["escape_down"]:
                        now = time.monotonic()
                        if now - state["escape_t1"] <= TRIPLE_ESCAPE_WINDOW:
                            for _vk in (0xA4, 0xA5, VK_MENU_CODE):
                                user32.keybd_event(_vk, 0, 0x0002, 0)
                            os._exit(0)
                        state["escape_t1"] = state["escape_t2"]
                        state["escape_t2"] = now
                        state["escape_down"] = True
                    elif key_up:
                        state["escape_down"] = False

                if vk_code in (VK_MENU_CODE, 0xA4, 0xA5):
                    if key_down:
                        state["alt_tap_start"] = time.monotonic()
                        state["alt_down"] = True
                    elif key_up:
                        if state["alt_tap_start"] and time.monotonic() - state["alt_tap_start"] < 0.3:
                            module_globals["dim_mode"] = not module_globals.get("dim_mode", False)
                        state["alt_tap_start"] = 0.0
                        state["alt_down"] = False

                # ── Ctrl+C → pass through + silently snap clipboard 80 ms later ──
                if vk_code == _vk_c and state["ctrl_down"] and key_down:
                    threading_module.Thread(target=_snap_clipboard, daemon=True).start()
                    # No return — fall through so the app copies normally.

                # ── Alt+V → swallow and inject stored text via scan codes ─────────
                if vk_code == _vk_v and state["alt_down"] and key_down:
                    state["alt_tap_start"] = 0.0   # it was a chord, not a tap — skip dim toggle
                    if module_globals.get("_stored"):
                        threading_module.Thread(target=type_stored_content, daemon=True).start()
                    else:
                        logger.info("Private clip: nothing stored yet — use Ctrl+C first.")
                    return 1

                if browser_privacy_active():
                    if vk_code == vk_capital:
                        return user32.CallNextHookEx(module_globals["hook_handle"], n_code, w_param, l_param)
                    if vk_code == vk_escape:
                        return 1
                    if vk_code in (VK_MENU_CODE, 0xA4, 0xA5):
                        return user32.CallNextHookEx(module_globals["hook_handle"], n_code, w_param, l_param)
                    forward_keyboard_to_browser(vk_code, scan_code, key_down)
                    return 1

                a_and_caps = state["a_down"] and state["capslock_key_down"]
                if a_and_caps:
                    if not is_capslock_on():
                        try_trigger_active_window_screenshot_and_open()
                    else:
                        reset_hotkey_state()

                if state["win_down"] and state["shift_down"] and state["s_down"]:
                    try_trigger_screenshot("win+shift+s-hook")

                both_down = state["ctrl_down"] and state["shift_down"]
                if both_down:
                    try_trigger_hotkey("ctrl+shift-hook")
                if not both_down and not a_and_caps:
                    reset_hotkey_state()

            return user32.CallNextHookEx(module_globals["hook_handle"], n_code, w_param, l_param)

        def mouse_proc(n_code: int, w_param: int, l_param: int) -> int:
            if n_code == hc_action and browser_privacy_active():
                mouse_info = ctypes_module.cast(l_param, ctypes_module.POINTER(mouse_struct)).contents
                if w_param == wm_lbuttondown:
                    state["mouse_left_down"] = True
                elif w_param == wm_lbuttonup:
                    state["mouse_left_down"] = False
                elif w_param == wm_rbuttondown:
                    state["mouse_right_down"] = True
                elif w_param == wm_rbuttonup:
                    state["mouse_right_down"] = False
                elif w_param == wm_mbuttondown:
                    state["mouse_middle_down"] = True
                elif w_param == wm_mbuttonup:
                    state["mouse_middle_down"] = False

                if w_param in {
                    wm_mousemove,
                    wm_mousewheel,
                    wm_lbuttondown,
                    wm_lbuttonup,
                    wm_rbuttondown,
                    wm_rbuttonup,
                    wm_mbuttondown,
                    wm_mbuttonup,
                }:
                    forward_mouse_message_to_browser(
                        w_param,
                        mouse_info.pt.x,
                        mouse_info.pt.y,
                        mouse_info.mouseData,
                        state,
                    )
                now = time.monotonic()
                if now - state["last_mouse_forward_log_time"] >= 1.0:
                    logger.info("Mirroring mouse movement and clicks into the browser while preserving normal mouse input.")
                    state["last_mouse_forward_log_time"] = now

            return user32.CallNextHookEx(module_globals["mouse_hook_handle"], n_code, w_param, l_param)

        hook_proc = hookproc_type(keyboard_proc)
        hook_handle = user32.SetWindowsHookExW(
            wh_keyboard_ll,
            hook_proc,
            module_globals["kernel32"].GetModuleHandleW(None),
            0,
        )
        if not hook_handle:
            raise ctypes_module.WinError()

        mouse_hook_proc = hookproc_type(mouse_proc)
        mouse_hook_handle = user32.SetWindowsHookExW(
            wh_mouse_ll,
            mouse_hook_proc,
            module_globals["kernel32"].GetModuleHandleW(None),
            0,
        )
        if not mouse_hook_handle:
            raise ctypes_module.WinError()

        module_globals["hook_proc"] = hook_proc
        module_globals["hook_handle"] = hook_handle
        module_globals["mouse_hook_proc"] = mouse_hook_proc
        module_globals["mouse_hook_handle"] = mouse_hook_handle

        logger.info("Patched global low-level keyboard and mouse hooks installed.")
        start_hotkey_poll_thread()

    module_globals["start_hotkey_poll_thread"] = start_hotkey_poll_thread
    module_globals["start_capslock_poll_thread"] = start_capslock_poll_thread
    module_globals["install_keyboard_hook"] = install_keyboard_hook


def main() -> None:
    if not PYC_PATH.exists():
        raise FileNotFoundError(f"Recovered opener cache not found: {PYC_PATH}")

    pyc_bytes = PYC_PATH.read_bytes()
    if len(pyc_bytes) <= PYC_HEADER_SIZE:
        raise RuntimeError(f"Recovered opener cache is unexpectedly short: {PYC_PATH}")

    code = marshal.loads(pyc_bytes[PYC_HEADER_SIZE:])
    globals_dict = {
        "__name__": "recovered_localhost_9999_opener",
        "__file__": str(WRAPPER_PATH),
        "__package__": None,
        "__cached__": str(PYC_PATH),
    }
    exec(code, globals_dict)
    patch_recovered_module(globals_dict)
    globals_dict["main"]()


if __name__ == "__main__":
    main()
