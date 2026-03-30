import random
import sys
from typing import List, Tuple


# Klasa pomocincza do budowy Grafu

class Graph:
    def __init__(self, n_vertices: int):
        self.n = n_vertices
        self.adj: List[List[Tuple[int, int]]] = [[] for _ in range(n_vertices)]

    def add_edge(self, u: int, v: int, w: int, undirected: bool = True) -> None:
        self.adj[u].append((v, w))
        if undirected:
            self.adj[v].append((u, w))


# Główna klasa
class Bajtolandia:
    def __init__(
            self,
            n: int = None,
            m: int = None,
            mapa_kosztow: List[List[int]] = None,
            start_pos: Tuple[int, int] = None,
            end_pos: Tuple[int, int] = None,
            n_min: int = 5, n_max: int = 15,
            m_min: int = 5, m_max: int = 15,
            min_cost: int = 1, max_cost: int = 9,
    ):
        # Konfiguracja mapy
        if mapa_kosztow is not None:
            self.n = len(mapa_kosztow)
            self.m = len(mapa_kosztow[0]) if self.n > 0 else 0
            self.cost = mapa_kosztow
        elif n is not None and m is not None:
            self.n = n
            self.m = m
            self.cost = [[random.randint(min_cost, max_cost) for _ in range(m)] for _ in range(n)]
        else:
            self.n = random.randint(n_min, n_max)
            self.m = random.randint(m_min, m_max)
            self.cost = [[random.randint(min_cost, max_cost) for _ in range(self.m)] for _ in range(self.n)]

        self.start = start_pos
        self.end = end_pos
        self.graph = None

        # Walidacja miast
        if self.start is not None and self.end is not None:
            self._waliduj_miasta()

    def _waliduj_miasta(self):
        sx, sy = self.start
        tx, ty = self.end

        if not (0 <= sx < self.n and 0 <= sy < self.m):
            raise ValueError(f"Start {self.start} poza planszą (max wiersz={self.n - 1}, max kol={self.m - 1})")
        if not (0 <= tx < self.n and 0 <= ty < self.m):
            raise ValueError(f"Cel {self.end} poza planszą (max wiersz={self.n - 1}, max kol={self.m - 1})")

        manhattan = abs(sx - tx) + abs(sy - ty)
        if manhattan == 0:
            raise ValueError("BŁĄD: Miasta są w tym samym punkcie!")
        if manhattan == 1:
            raise ValueError("BŁĄD: Miasta sąsiadują ze sobą (zgodnie z zasadami muszą być oddalone)!")

    def _cell_id(self, i: int, j: int) -> int:
        return i * self.m + j

    def _coords_from_id(self, vid: int) -> Tuple[int, int]:
        return divmod(vid, self.m)

    def losuj_miasta(self) -> None:
        if self.start and self.end:
            return
        while True:
            sx, sy = random.randint(0, self.n - 1), random.randint(0, self.m - 1)
            tx, ty = random.randint(0, self.n - 1), random.randint(0, self.m - 1)
            if abs(sx - tx) + abs(sy - ty) > 1:
                self.start = (sx, sy)
                self.end = (tx, ty)
                break

    def build_graph(self) -> None:
        self.graph = Graph(self.n * self.m)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i in range(self.n):
            for j in range(self.m):
                u = self._cell_id(i, j)
                for dx, dy in dirs:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < self.n and 0 <= nj < self.m:
                        v = self._cell_id(ni, nj)
                        w = self.cost[ni][nj]
                        self.graph.add_edge(u, v, w, undirected=False)

    # Algorytm Dijkstry
    def dijkstra(self, start_id: int):
        if self.graph is None:
            raise ValueError("Najpierw zbuduj graf!!!")

        n_vertices = self.graph.n
        INF = 10 ** 18

        dist = [INF] * n_vertices
        prev = [-1] * n_vertices
        visited = [False] * n_vertices

        dist[start_id] = self._start_cost(start_id)

        for _ in range(n_vertices):
            # znajdź wierzchołek o najmniejszym dist[] spośród nieodwiedzonych
            v = -1
            best = INF
            for i in range(n_vertices):
                if not visited[i] and dist[i] < best:
                    best = dist[i]
                    v = i

            if v == -1:
                break  # nie ma czego odwiedzać

            visited[v] = True

            for neigh, w in self.graph.adj[v]:
                if visited[neigh]:
                    continue

                nd = dist[v] + w
                if nd < dist[neigh]:
                    dist[neigh] = nd
                    prev[neigh] = v

        return dist, prev

    def _start_cost(self, sid: int) -> int:
        r, c = self._coords_from_id(sid)
        return self.cost[r][c]

    def znajdz_najtansza_trase(self):
        if not self.start:
            self.losuj_miasta()
        if not self.graph:
            self.build_graph()

        sid = self._cell_id(*self.start)
        tid = self._cell_id(*self.end)
        dist, prev = self.dijkstra(sid)

        if dist[tid] >= 10 ** 18:
            return [], -1

        path = []
        curr = tid
        while curr != -1:
            path.append(curr)
            curr = prev[curr]

        path_coords = [self._coords_from_id(v) for v in reversed(path)]
        return path_coords, dist[tid]

    # WIZUALIZACJA

    def weryfikacja_kosztu(self, path, total_cost):
        if not path:
            return

        skladowe = []
        suma_check = 0
        for (r, c) in path:
            val = self.cost[r][c]
            skladowe.append(str(val))
            suma_check += val

        rownanie = " + ".join(skladowe)
        print(f"\n KOSZT TRASY:")
        print(f"    Koszty pól na trasie: {rownanie} = {suma_check}")

    def _get_cell_width(self):
        max_num = max(self.n, self.m, 9)
        max_c = 0
        for row in self.cost:
            max_c = max(max_c, max(row))
        max_val = max(max_num, max_c)
        return len(str(max_val)) + 1

    def wypisz_koszty(self):
        print(f"\n--- MAPA KOSZTÓW ---")
        w = self._get_cell_width()

        print(f"Wymiary: {self.n} wierszy x {self.m} kolumn")

        line_len = (w + 1) * self.m + 8
        print("-" * line_len)

        for i in range(self.n):
            row_vals = [self.cost[i][j] for j in range(self.m)]
            row_str = " ".join(f"{x:{w}}" for x in row_vals)
            print(f"| {row_str} | Wiersz {i}")

        print("-" * line_len)

        idx_str = " ".join(f"{j:{w}}" for j in range(self.m))
        print(f"  {idx_str}   (Kolumny)")

    def wypisz_miasta(self):
        print(f"\nLOKALIZACJA MIAST")
        print(f"Start: {self.start} (Koszt pola: {self.cost[self.start[0]][self.start[1]]})")
        print(f"Cel:   {self.end} (Koszt pola: {self.cost[self.end[0]][self.end[1]]})")

    @staticmethod
    def wypisz_trase_tekstowo(path):
        if not path:
            print("Brak trasy.")
            return
        str_path = " -> ".join([f"(W:{r}, K:{c})" for r, c in path])
        print(f"\n>>> PRZEBIEG TRASY:\n{str_path}")

    def rysuj_trase_na_planszy(self, path):
        grid = [['.' for _ in range(self.m)] for _ in range(self.n)]
        for r, c in path:
            grid[r][c] = '#'
        if self.start:
            grid[self.start[0]][self.start[1]] = 'S'
        if self.end:
            grid[self.end[0]][self.end[1]] = 'T'

        print("\nWIZUALIZACJA TRASY")
        print("(S = Start, T = Cel, # = Trasa)")

        w = self._get_cell_width()
        line_len = (w + 1) * self.m + 8
        print("-" * line_len)

        for i in range(self.n):
            row_str = " ".join(f"{grid[i][j]:>{w}}" for j in range(self.m))
            print(f"| {row_str} | Wiersz {i}")

        print("-" * line_len)

        idx_str = " ".join(f"{j:{w}}" for j in range(self.m))
        print(f"  {idx_str}")


def pobierz_liczbe(msg):
    while True:
        try:
            val = int(input(msg))
            if val < 1:
                print("Liczba musi być dodatnia!")
                continue
            return val
        except ValueError:
            print("To nie jest liczba.")


def pobierz_wiersz_kosztow(idx, m):
    while True:
        try:
            line = input(f"Podaj koszty dla wiersza {idx} ({m} liczb): ")
            vals = list(map(int, line.strip().split()))
            if len(vals) != m:
                print(f"Błąd! Wymagane {m} liczb.")
                continue
            return vals
        except ValueError:
            print("Błąd! Użyj liczb całkowitych oddzielonych spacją.")


def pobierz_punkt(nazwa, n, m):
    while True:
        try:
            line = input(f"Podaj {nazwa} (Wiersz Kolumna): ")
            coords = list(map(int, line.strip().split()))
            if len(coords) != 2:
                print("Podaj dwie liczby!")
                continue
            r, c = coords
            if 0 <= r < n and 0 <= c < m:
                return r, c

            print(f"Poza zakresem! Wiersze 0-{n - 1}, Kolumny 0-{m - 1}.")
        except ValueError:
            print("Błąd formatu!")


def main():
    print("\n" + "=" * 45)
    print("      BAJTOLANDIA - OPTYMALIZACJA TRASY")
    print("=" * 45)
    print("1. Wpisz wszytkie dane ręcznie")
    print("2. Własne wymiary, ale losowe koszty")
    print("3. Wszystko losowe")
    print("4. Wyjście")

    wybor = input("\nWybór: ").strip()
    if wybor == '4':
        sys.exit()

    try:
        if wybor == '3':
            baj = Bajtolandia()
        elif wybor in ['1', '2']:
            n = pobierz_liczbe("Liczba wierszy: ")
            m = pobierz_liczbe("Liczba kolumn: ")

            if wybor == '1':
                print(f"\nWprowadzanie kosztów:")
                mapa = []
                for i in range(n):
                    mapa.append(pobierz_wiersz_kosztow(i, m))
                baj = Bajtolandia(mapa_kosztow=mapa)
            else:
                baj = Bajtolandia(n=n, m=m)
                baj.wypisz_koszty()

            print("\n--- Konfiguracja Miast ---")
            print("1. Podam własne współrzędne")
            print("2. Wylosuj")
            if input("Wybór: ").strip() == '1':
                start = pobierz_punkt("START", n, m)
                end = pobierz_punkt("CEL", n, m)
                if baj.cost:
                    baj = Bajtolandia(mapa_kosztow=baj.cost, start_pos=start, end_pos=end)
            else:
                baj.losuj_miasta()
        else:
            return

        print("\nObliczanie najtańszej trasy...")
        baj.build_graph()
        path, cost = baj.znajdz_najtansza_trase()

        if path:
            baj.wypisz_miasta()
            baj.wypisz_koszty()
            baj.wypisz_trase_tekstowo(path)
            baj.rysuj_trase_na_planszy(path)

            baj.weryfikacja_kosztu(path, cost)

            print("\n" + "*" * 40)
            print(f"*** CAŁKOWITY KOSZT TRASY: {cost} ***")
            print("*" * 40)
        else:
            print("\n!!! Nie znaleziono trasy (graf niespójny?) !!!")

    except ValueError as e:
        print(f"\nBŁĄD: {e}")
    except Exception as e:
        print(f"\nBŁĄD KRYTYCZNY: {e}")


if __name__ == "__main__":
    print('Tworzymy mape z dwoma wyróżnionymi miastami: BAJTOGÓRA i BAJTOLANDIA')
    print('Chcemy znaleźć najtańszą trasę pomiędzy tymi miastami')
    print('UWAGI PRZY WYBORZE MIAST')
    print('Miasta nie mogą być w tym samym miesjcu jak i sąsiadować ze sobą')
    print('Można również samemu wybrać rozmiar mapy, pozycje wyróżnionych miast jak i koszty dróg')
    print('Ale można też te czynności zrobić automatycznie')
    print('Jeżeli wpiszujesz więcej niż jedną liczbę użyj spacji NIE przecinka')
    while True:
        main()
        if input("\nPonowić? (t/n): ").lower() != 't':
            break
