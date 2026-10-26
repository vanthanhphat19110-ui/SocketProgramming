/*
 * Manual input-line redraw in C++ (same idea as option_b_manual_redraw.py)
 * -------------------------------------------------------------------------
 * No real network. A fake "receiver" thread pretends to be Minh and sends
 * a message every 3-6 seconds, while you type at any time.
 *
 * Build:
 *   Windows (MinGW):  g++ -std=c++17 chat_redraw.cpp -o chat_redraw.exe
 *   Windows (MSVC):   cl /std:c++17 /EHsc chat_redraw.cpp
 *   Linux/macOS:      g++ -std=c++17 -pthread chat_redraw.cpp -o chat_redraw
 * Type /quit to exit.
 *
 * How it works:
 *   - Main thread reads ONE key at a time and keeps typed text in `buffer`.
 *   - When a message arrives, the receiver thread:
 *       1. erases the input line   ("\r" + "\033[K")
 *       2. prints the message + newline
 *       3. redraws "> " + buffer   (half-typed text is not lost)
 *   - `screen_mutex` ensures only one thread writes to the screen at a time.
 */
#include <atomic>
#include <chrono>
#include <cstdio>
#include <iostream>
#include <mutex>
#include <random>
#include <string>
#include <thread>

#ifdef _WIN32
  #include <conio.h>
  #include <windows.h>
#else
  #include <termios.h>
  #include <unistd.h>
#endif

// ---------------------------------------------------------------------------
// Terminal helpers: read a single key without waiting for Enter
// ---------------------------------------------------------------------------
#ifdef _WIN32
static void setup_terminal() {
    // Enable ANSI escape codes (\033[K) in the Windows console
    HANDLE out = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD mode = 0;
    GetConsoleMode(out, &mode);
    SetConsoleMode(out, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
}
static void restore_terminal() {}

// Returns the key, or -1 for keys we ignore (arrows, F1..F12)
static int get_key() {
    int ch = _getch();
    if (ch == 0 || ch == 0xE0) {   // special keys send 2 codes
        _getch();                  // read and ignore the second code
        return -1;
    }
    return ch;
}
#else
static termios g_old_settings;

static void setup_terminal() {
    tcgetattr(STDIN_FILENO, &g_old_settings);
    termios raw = g_old_settings;
    raw.c_lflag &= ~(ICANON | ECHO);   // keys arrive one by one, no echo
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
}
static void restore_terminal() {
    tcsetattr(STDIN_FILENO, TCSANOW, &g_old_settings);
}
static int get_key() {
    char c;
    if (read(STDIN_FILENO, &c, 1) != 1) return 3;   // treat EOF as Ctrl+C
    if (c == 27) {                                  // arrow keys: ESC [ A
        char seq[2];
        read(STDIN_FILENO, seq, 2);
        return -1;
    }
    return static_cast<unsigned char>(c);
}
#endif

// ---------------------------------------------------------------------------
// Shared state
// ---------------------------------------------------------------------------
static const std::string PROMPT     = "> ";
static const std::string CLEAR_LINE = "\r\033[K";   // start of line + erase

static std::string       buffer;                    // text typed so far
static std::mutex        screen_mutex;
static std::atomic<bool> running{true};

// Print a line ABOVE the input line, then redraw prompt + typed text.
// Safe to call from any thread (receiver, file sender, UDP listener...).
static void show_message(const std::string& line) {
    std::lock_guard<std::mutex> lock(screen_mutex);
    std::cout << CLEAR_LINE            // 1. erase input line
              << line << "\n"          // 2. print the message
              << PROMPT << buffer      // 3. redraw prompt + typed text
              << std::flush;
}

// ---------------------------------------------------------------------------
// Fake receiver thread (replaces the real TCP recv() loop)
// ---------------------------------------------------------------------------
static void fake_receiver(const std::string name) {
    const char* messages[] = {
        "Hi Quan, are you there?",
        "Did you finish the slides?",
        "ok, which part?",
        "I will check it again",
        "see you at the demo!",
    };
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<int> delay_ms(3000, 6000);
    std::uniform_int_distribution<int> pick(0, 4);

    while (running) {
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms(rng)));
        if (!running) break;
        // Real app: n = recv(sock, buf, sizeof buf, 0); show_message("[" + name + "] " + buf);
        show_message("[" + name + "] " + messages[pick(rng)]);
    }
}

// ---------------------------------------------------------------------------
// Main thread: keyboard loop
// ---------------------------------------------------------------------------
int main() {
    const std::string me = "Quan";

    std::cout << "[*] Connected to Minh (fake). Type messages, /quit to exit.\n";
    setup_terminal();

    std::thread receiver(fake_receiver, std::string("Minh"));
    receiver.detach();   // daemon-like: we don't wait for it on exit

    std::cout << PROMPT << std::flush;

    while (true) {
        int ch = get_key();
        if (ch == -1) continue;

        std::lock_guard<std::mutex> lock(screen_mutex);

        if (ch == '\r' || ch == '\n') {                 // Enter -> send
            std::string text = buffer;
            buffer.clear();
            if (text == "/quit") {
                std::cout << "\n";
                break;
            }
            std::cout << CLEAR_LINE;
            if (!text.empty()) {
                std::cout << "[" << me << "] " << text << "\n";
                // Real app: send(sock, text.c_str(), text.size(), 0);
            }
            std::cout << PROMPT;
        } else if (ch == 8 || ch == 127) {              // Backspace
            if (!buffer.empty()) {
                buffer.pop_back();
                std::cout << "\b \b";                   // back, erase, back
            }
        } else if (ch == 3) {                           // Ctrl+C
            std::cout << "\n";
            break;
        } else if (ch >= 32 && ch < 127) {              // printable ASCII
            buffer += static_cast<char>(ch);
            std::cout << static_cast<char>(ch);
        }
        std::cout << std::flush;
    }

    running = false;
    restore_terminal();
    std::cout << "[*] Bye!" << std::endl;
    return 0;
}
