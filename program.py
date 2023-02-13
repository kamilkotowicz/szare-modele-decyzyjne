# Aplikacja została napisana na Wydziale Informatyki Politechniki Białostockiej.
# Autorem programu jest Kamil Kotowicz.
# Program jest częścią pracy dyplomowej "Szare modele decyzyjne – procedura oraz przykład zastosowania".
import csv
import numpy as np
import math
import sys


def wczytaj_macierz(sciezka):
    with open(sciezka, 'r') as plik_in:
        reader = csv.reader(plik_in, delimiter=';', quotechar='"')
        next(reader)
        data = [data for data in reader]
    data_array = np.asarray(data, dtype=float)
    return data_array


def wczytaj_nazwy(sciezka):
    with open(sciezka, 'r') as plik_in:
        reader = csv.reader(plik_in, delimiter=';', quotechar='"')
        header = next(reader)
    return header


def wczytaj_dane():
    wagi_kryteriow_decyzyjnych = wczytaj_macierz('wagi_kryteriow.csv')
    szara_macierz_decyzyjna = wczytaj_macierz('macierz_wejsciowa.csv')
    nazwy_produktow = wczytaj_nazwy("nazwy_produktow.csv")
    return wagi_kryteriow_decyzyjnych, szara_macierz_decyzyjna, nazwy_produktow


def pisz_wynik(sciezka, wynik):
    open(sciezka, 'w').close()
    with open(sciezka, 'a') as plik_out:
        for i, wiersz in enumerate(wynik):
            plik_out.write(str(i+1) + ';' + wiersz[0] + ';' + str(wiersz[1])+'\n')


def podziel_na_dwie_macierze(znormalizowana_macierz_decyzyjna, liczba_kolumn):
    znormalizowana_min = np.empty((0, liczba_kolumn), dtype=float)
    znormalizowana_max = np.empty((0, liczba_kolumn), dtype=float)
    for indeks, wiersz in enumerate(znormalizowana_macierz_decyzyjna):
        if indeks % 2 == 0:
            znormalizowana_min = np.vstack([znormalizowana_min, wiersz])
        else:
            znormalizowana_max = np.vstack([znormalizowana_max, wiersz])
    return znormalizowana_min, znormalizowana_max


def oblicz_odleglosci(wazona_min, wazona_max, wzorzec_min, wzorzec_max, antywzorzec_min, antywzorzec_max, liczba_kolumn, liczba_wierszy):
    odleglosci_do_wzorca = np.empty((liczba_wierszy, liczba_kolumn), dtype=float)
    odleglosci_do_antywzorca = np.empty((liczba_wierszy, liczba_kolumn), dtype=float)
    for i in range(liczba_wierszy):
        for j in range(liczba_kolumn):
            odleglosci_do_wzorca[i][j] = math.sqrt(((wazona_min[i][j]-wzorzec_min[j]) ** 2 + (wazona_max[i][j]-wzorzec_max[j]) ** 2)/2)
            odleglosci_do_antywzorca[i][j] = math.sqrt(((wazona_min[i][j]-antywzorzec_min[j]) ** 2 + (wazona_max[i][j]-antywzorzec_max[j]) ** 2)/2)
    return odleglosci_do_wzorca, odleglosci_do_antywzorca


def porownaj_liczby_szare(min1, max1, min2, max2):
    suma_dlugosci = (max1-min1) + (max2-min2)
    return max(0, suma_dlugosci - max(0, max1-min2)) / suma_dlugosci


def oblicz_rating_grey(wazona_min, wazona_max, wzorzec_min, wzorzec_max, liczba_kolumn, liczba_wierszy):
    rating_grey = np.empty(liczba_wierszy, dtype=float)
    for i in range(liczba_wierszy):
        suma_prawdopodobienstw = 0
        for j in range(liczba_kolumn):
            prawdopodobienstwo = porownaj_liczby_szare(wazona_min[i][j], wazona_max[i][j], wzorzec_min[j], wzorzec_max[j])
            #print(prawdopodobienstwo)
            suma_prawdopodobienstw += prawdopodobienstwo
        rating_grey[i] = suma_prawdopodobienstw / liczba_kolumn
    return rating_grey


def wyswietl_obliczenia(maks_w_kolumnie, znormalizowana_min, znormalizowana_max, wazona_min, wazona_max, wzorzec_min,
                        wzorzec_max, antywzorzec_min, antywzorzec_max, odleglosci_do_wzorca, odleglosci_do_antywzorca,
                        calkowita_odleglosc_do_wzorca, calkowita_odleglosc_do_antywzorca, rating_topsis, rating_grey):
    print(f"Maksymalne wartości w kolumnie\n{maks_w_kolumnie}")
    print(f"Znormalizowana macierz decyzyjna, dolna granica przedziału\n{znormalizowana_min}")
    print(f"Znormalizowana macierz decyzyjna, górna granica przedziału\n{znormalizowana_max}")
    print(f"Ważona macierz decyzyjna, dolna granica\n{wazona_min}")
    print(f"Ważona macierz decyzyjna, górna granica\n{wazona_max}")
    print(f"Dolna granica wzorca\n{wzorzec_min}")
    print(f"Górna granica wzorca\n{wzorzec_max}")
    print(f"Dolna granica antywzorca\n{antywzorzec_min}")
    print(f"Górna granica antywzorca\n{antywzorzec_max}")
    print(f"Odleglosci do wzorca\n{odleglosci_do_wzorca}")
    print(f"Odleglosci do antywzorca\n{odleglosci_do_antywzorca}")
    print(f"Suma odleglosci do wzorca\n{calkowita_odleglosc_do_wzorca}")
    print(f"Suma odleglosci do antywzorca\n{calkowita_odleglosc_do_antywzorca}")
    print(f"Rating topsis\n{rating_topsis}")
    print(f"Rating grey\n{rating_grey}")


def grey_topsis(wagi_kryteriow_decyzyjnych, szara_macierz_decyzyjna):
    liczba_kolumn = len(szara_macierz_decyzyjna[0])
    liczba_wierszy = len(szara_macierz_decyzyjna) // 2
    # normalizacja macierzy decyzyjnej
    maks_w_kolumnie = np.max(szara_macierz_decyzyjna, axis=0)
    znormalizowana_macierz_decyzyjna = szara_macierz_decyzyjna / maks_w_kolumnie
    znormalizowana_min, znormalizowana_max = podziel_na_dwie_macierze(znormalizowana_macierz_decyzyjna, liczba_kolumn)
    # obliczanie wazonej macierzy decyzyjnej
    wazona_min = np.vstack([element * wagi_kryteriow_decyzyjnych[0] for element in znormalizowana_min])
    wazona_max = np.vstack([element * wagi_kryteriow_decyzyjnych[1] for element in znormalizowana_max])
    # znalezienie wzorca i antywzorca
    wzorzec_min = np.max(wazona_min, axis=0)
    wzorzec_max = np.max(wazona_max, axis=0)
    antywzorzec_min = np.min(wazona_min, axis=0)
    antywzorzec_max = np.min(wazona_max, axis=0)
    # obliczenie odleglosci i ratingu
    odleglosci_do_wzorca, odleglosci_do_antywzorca = oblicz_odleglosci(wazona_min, wazona_max, wzorzec_min, wzorzec_max, antywzorzec_min, antywzorzec_max, liczba_kolumn, liczba_wierszy)
    calkowita_odleglosc_do_wzorca = np.sum(odleglosci_do_wzorca, axis=1)
    calkowita_odleglosc_do_antywzorca = np.sum(odleglosci_do_antywzorca, axis=1)
    # obliczenie ratingu metodą topsis
    rating_topsis = calkowita_odleglosc_do_antywzorca / (calkowita_odleglosc_do_antywzorca + calkowita_odleglosc_do_wzorca)
    # obliczenie ratingu metodą grey
    rating_grey = oblicz_rating_grey(wazona_min, wazona_max, wzorzec_min, wzorzec_max, liczba_kolumn, liczba_wierszy)
    # wyswietlenie wynikow obliczen
    wyswietl_obliczenia(maks_w_kolumnie, znormalizowana_min, znormalizowana_max, wazona_min, wazona_max, wzorzec_min,
                        wzorzec_max, antywzorzec_min, antywzorzec_max, odleglosci_do_wzorca, odleglosci_do_antywzorca,
                        calkowita_odleglosc_do_wzorca, calkowita_odleglosc_do_antywzorca, rating_topsis, rating_grey)
    return rating_topsis, rating_grey


def main():
    try:
        wagi_kryteriow_decyzyjnych, szara_macierz_decyzyjna, nazwy_produktow = wczytaj_dane()
        rating_topsis, rating_grey = grey_topsis(wagi_kryteriow_decyzyjnych, szara_macierz_decyzyjna)
        produkty_topsis = np.vstack([nazwy_produktow, rating_topsis]).T
        pisz_wynik("uzyskany_ranking_topsis.csv", produkty_topsis[produkty_topsis[:, 1].argsort()][::-1])
        produkty_grey = np.vstack([nazwy_produktow, rating_grey]).T
        pisz_wynik("uzyskany_ranking_grey.csv", produkty_grey[produkty_grey[:, 1].argsort()])
    except ValueError:
        print("Podano niepoprawne dane w pliku")
    sys.stdin.readline()

if __name__ == "__main__":
    main()