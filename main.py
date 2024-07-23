from json import loads as json_loads
from enum import StrEnum
from http.client import HTTPSConnection
from random import choice
from threading import Thread

SQUARE = "\u25a0"
DOT = "\u25cf"

COLORS = {
    "1": ({"en": "Yellow", "fr": "Jaune", "es": "Amarillo", "jp": "黄色", "it": "Giallo", "de": "Gelb"}, "\033[93m"),
    "2": ({"en": "Blue", "fr": "Bleu", "es": "Azul", "jp": "青", "it": "Blu", "de": "Blau"}, "\033[94m"),
    "3": ({"en": "Red", "fr": "Rouge", "es": "Rojo", "jp": "赤", "it": "Rosso", "de": "Rot"}, "\033[91m"),
    "4": ({"en": "Green", "fr": "Vert", "es": "Verde", "jp": "緑", "it": "Verde", "de": "Grün"}, "\033[32m"),
    "5": ({"en": "White", "fr": "Blanc", "es": "Blanco", "jp": "白", "it": "Bianco", "de": "Weiß"}, "\033[97m"),
    "6": ({"en": "Magenta", "fr": "Magenta", "es": "Magenta", "jp": "マゼンタ", "it": "Magenta", "de": "Magenta"}, "\033[95m"),
}
RESET = "\033[0m"


class Language(StrEnum):
    EN = "en"
    FR = "fr"
    ES = "es"
    JP = "jp"
    IT = "it"
    DE = "de"

    @classmethod
    def to_dict(cls) -> dict[str, str]:
        return {str(i + 1): lang.value for i, lang in enumerate(cls)}


class Mastermind:
    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns
        Thread(target=self.fetch_translations, args=()).start()
        self.language = self.choose_language()
        self.secret_combination = self.generate_secret_combination()

    def choose_language(self) -> str:
        print("\nChoose your language / Choisissez votre langue / Elige tu idioma / 言語を選択してください / Scegli la tua lingua / Wähle deine Sprache")
        print("[1] English\n[2] Français\n[3] Español\n[4] 日本語\n[5] Italiano\n[6] Deutsch")
        choice = input("\nEnter the number / Entrez le numéro / Ingrese el número / 数字を入力してください / Inserisci il numero / Gib die Zahl ein: ").strip()
        languages = Language.to_dict()
        return languages.get(choice, "en")

    def fetch_translations(self) -> dict[str, str]:
        host = "raw.githubusercontent.com"
        path = "/Macktireh/mastermind/main/translations.json"
        conn = HTTPSConnection(host)
        conn.request("GET", path)
        response = conn.getresponse().read()
        self.translations = json_loads(response.decode("utf-8"))
        conn.close()

    def generate_secret_combination(self) -> list[str]:
        return [choice(list(COLORS)) for _ in range(4)]

    def display_combination(self, combination: list[str], symbol: str = SQUARE, separator: str = " ") -> str:
        return separator.join(f"{COLORS[c][1]}{symbol}{RESET}" for c in combination)

    def check_combination(self, guess: str) -> tuple[int, int]:
        red = sum(1 for s, g in zip(self.secret_combination, guess, strict=False) if s == g)
        white = sum(min(self.secret_combination.count(j), guess.count(j)) for j in set(guess)) - red
        return red, white

    def print_instructions(self) -> None:
        lang = self.language
        trans = self.translations[lang]
        instructions = f"\n\n{'='*100}\n{' '*5}{trans['game_title']}{' '*10}\n{'='*100}\n\n{''.join(trans['instructions'])}"
        color_options = trans["color_options"] + " ".join(
            f"{COLORS[key][1]}[{key}]: {COLORS[key][0][lang]}{RESET}" for key in COLORS
        )
        print(instructions + color_options + "\n")

    def play_round(self) -> bool:
        lang = self.language
        trans = self.translations[lang]
        turn = 1
        while turn <= self.max_turns:
            guess = input(trans["input_prompt"].format(turn=turn, max_turns=self.max_turns)).strip()
            if len(guess) == 4 and set(guess).issubset(COLORS):
                red, white = self.check_combination(guess)
                red_indicators = self.display_combination(["3"] * red, symbol=DOT)
                white_indicators = self.display_combination(["5"] * white, symbol=DOT)
                indicators = f"{trans['indicators_label']}: {red_indicators} {white_indicators}".strip()
                print(f"{self.display_combination(list(guess))}  {indicators}\n")
                if red == 4:
                    print(f"✅  {COLORS['4'][1]}{trans['win_message']} {RESET}\n")
                    return True
                turn += 1
            else:
                print(f"❌  {COLORS['3'][1]}{trans['input_error']} {RESET}\n")
        return False

    def play(self) -> None:
        self.print_instructions()
        if not self.play_round():
            print(f"{self.translations[self.language]['lose_message']}{self.display_combination(self.secret_combination)}\n")


if __name__ == "__main__":
    Mastermind().play()
