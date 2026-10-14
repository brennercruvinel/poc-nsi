# Inventário de aliases do gabarito

Riscos de casamento por linha do gabarito, após normalização. Gerado por `src/audit_inventory.py`.

- Linhas: 120. Com alias de até 3 caracteres: 85. Com alias igual ao literal: 61. Com alias idêntico ao de uma leitura concorrente: 16. Com alias contido em alias concorrente, ou vice-versa: 7. Descritivos (DNS): 2.

| id | papel | label | aliases | curtos | = literal | idêntico ao concorrente | contido no concorrente |
|---|---|---|---:|---|---|---|---|
| ARU\|lng/ioc | collision | Aruba | 5 | ABW, aw |  |  | aruba ~ aruba airlines (trp/ica2) |
| FIJ\|lng/ioc | control | Fiji | 9 | FJI, fj |  |  |  |
| ARU\|trp/iata | collision | Araçatuba Airport | 3 | ARU | ARU |  |  |
| SLJ\|trp/iata | control | Solomon Airport | 4 | SLJ | SLJ |  |  |
| BRU\|lng/ioc | collision | Brunei Darussalam | 6 | BRN, bn |  |  |  |
| KUW\|lng/ioc | control | Kuwait | 4 | KWT, kw |  |  |  |
| BRU\|trp/iata | collision | Brussels Airport | 5 |  |  |  |  |
| YHZ\|trp/iata | control | Halifax / Stanfield International Airport | 7 | YHZ | YHZ |  |  |
| BRU\|trp/ica2 | collision | Belavia Belarusian Airlines | 6 | B2, BRU | BRU |  |  |
| RZO\|trp/ica2 | control | SATA International | 5 | S4 |  |  |  |
| GTM\|lng/i31 | collision | Guatemala | 5 | GT, GTM, gt | GTM |  |  |
| JEY\|lng/i31 | control | Jersey | 16 | JE, je |  |  |  |
| GTM\|fin/tck | collision | ZoomInfo Technologies Inc. | 5 |  |  |  |  |
| NEM\|fin/tck | control | NEWMONT Corp /DE/ | 4 |  |  |  |  |
| MYA\|lng/ioc | collision | Myanmar | 4 | MMR |  |  |  |
| NEP\|lng/ioc | control | Nepal | 35 | NPL |  |  |  |
| MYA\|trp/iata | collision | Moruya Airport | 5 | MYA | MYA |  |  |
| DEZ\|trp/iata | control | Deir ez-Zor Airport | 4 | DEZ | DEZ |  |  |
| MYA\|trp/ica2 | collision | Myflug | 2 |  |  |  |  |
| TFK\|trp/ica2 | control | Transafrik International | 1 |  |  |  |  |
| OMA\|lng/ioc | collision | Oman | 6 | OMN, om, omn |  |  | oman ~ oman air (trp/ica2); oman ~ oman airline (trp/ica2) |
| NED\|lng/ioc | control | Netherlands | 8 | NL, NLD |  |  |  |
| OMA\|trp/ica2 | collision | Oman Air | 3 | WY |  |  | oman air ~ oman (lng/ioc); oman airline ~ oman (lng/ioc) |
| XAX\|trp/ica2 | control | AirAsia X | 6 | D7 |  |  |  |
| OMA\|trp/iata | collision | Eppley Airfield | 4 | OMA | OMA |  |  |
| CTU\|trp/iata | control | Chengdu Shuangliu International Airport | 5 | CTU | CTU |  |  |
| TCA\|lng/i31 | collision | Turks and Caicos Islands | 6 | TC, TCI, tc |  |  |  |
| GIN\|lng/i31 | control | Guinea | 6 | GN, GUI, gn |  |  |  |
| TCA\|trp/iata | collision | Tennant Creek Airport | 4 | TCA | TCA |  |  |
| YPG\|trp/iata | control | Portage-la-Prairie / Southport Airport | 5 | YPG | YPG |  |  |
| VAN\|lng/ioc | collision | Vanuatu | 7 | VAN, VUT, van, vu, vut | VAN, van | van = trp/iata | van ~ van ferit melen (trp/iata); van ~ van ferit melen airport (trp/iata) |
| GEQ\|lng/ioc | control | Equatorial Guinea | 6 | EQG, GEQ, GNQ, gq | GEQ |  |  |
| VAN\|trp/iata | collision | Van Ferit Melen Airport | 5 | VAN | VAN | van = lng/ioc | van ferit melen airport ~ van (lng/ioc); van ferit melen ~ van (lng/ioc) |
| HOF\|trp/iata | control | Al-Ahsa International Airport | 5 | HOF | HOF |  |  |
| VIE\|lng/ioc | collision | Viet Nam | 9 | SRV, VIE, VN, VNM | VIE | vie = trp/iata |  |
| VIE\|trp/iata | collision | Vienna International Airport | 6 | VIE | VIE | vie = lng/ioc |  |
| GMP\|trp/iata | control | Gimpo International Airport | 5 | GMP | GMP |  |  |
| ALL\|fin/tck | collision | ALLSTATE CORP | 4 |  |  |  |  |
| VYX\|fin/tck | control | NCR Voyix Corp | 7 |  |  |  |  |
| ALL\|fin/i42 | collision | Lek | 3 | ALL, Lek | ALL |  |  |
| JOD\|fin/i42 | control | Jordanian Dinar | 3 |  |  |  |  |
| COP\|fin/tck | collision | CONOCOPHILLIPS | 4 |  |  |  |  |
| XOM\|fin/tck | control | EXXON MOBIL CORP | 3 |  |  |  |  |
| COP\|fin/i42 | collision | Colombian Peso | 8 | $, CO$ |  |  |  |
| QAR\|fin/i42 | control | Qatari Rial | 3 |  |  |  |  |
| CUP\|fin/i42 | collision | Cuban Peso | 3 | CUP | CUP | cup = trp/iata |  |
| XAG\|fin/i42 | control | Silver | 6 | XAG | XAG |  |  |
| CUP\|trp/iata | collision | General Francisco Bermúdez Airport | 6 | CUP | CUP | cup = fin/i42 |  |
| BJB\|trp/iata | control | Bojnord Airport | 3 | BJB | BJB |  |  |
| CVE\|fin/i42 | collision | Cabo Verde Escudo | 3 |  |  |  |  |
| JMD\|fin/i42 | control | Jamaican Dollar | 6 | $, J$, JMD, Jay | JMD |  |  |
| CVE\|trp/ica2 | collision | Cabo Verde Express | 1 |  |  |  |  |
| HJA\|trp/ica2 | control | Air Haiti | 2 |  |  |  |  |
| HTG\|fin/i42 | collision | Gourde | 5 | HTG | HTG | htg = trp/iata |  |
| FJD\|fin/i42 | control | Fiji Dollar | 3 |  |  |  |  |
| HTG\|trp/iata | collision | Khatanga Airport | 3 | HTG | HTG | htg = fin/i42 |  |
| GBW\|trp/iata | control | Ginbata Airport | 2 |  |  |  |  |
| KPW\|fin/i42 | collision | North Korean Won | 2 |  |  |  |  |
| IQD\|fin/i42 | control | Iraqi Dinar | 3 | ID |  |  |  |
| KPW\|trp/iata | collision | Keperveem Airport | 4 | KPW | KPW |  |  |
| OJU\|trp/iata | control | Tanjung Api Airport | 2 |  |  |  |  |
| RON\|fin/i42 | collision | Romanian Leu | 5 | L, RON | RON | ron = trp/iata |  |
| NZD\|fin/i42 | control | New Zealand Dollar | 6 | NZ$, NZD | NZD |  |  |
| RON\|trp/ica2 | collision | Nauru Air Corporation | 5 | ON |  |  |  |
| VTA\|trp/ica2 | control | Air Tahiti | 2 | VT |  |  |  |
| RON\|trp/iata | collision | Juan Jose Rondon Airport | 5 | RON | RON | ron = fin/i42 |  |
| GRW\|trp/iata | control | Graciosa Airport | 3 | GRW | GRW |  |  |
| SBD\|trp/iata | collision | San Bernardino International Airport | 3 | SBD | SBD |  |  |
| NWI\|trp/iata | control | Norwich Airport | 5 | NWI | NWI |  |  |
| SBD\|fin/i42 | collision | Solomon Islands Dollar | 3 |  |  |  |  |
| DJF\|fin/i42 | control | Djibouti Franc | 3 | DJF | DJF |  |  |
| DTE\|fin/tck | collision | DTE ENERGY CO | 4 | DTE | DTE | dte = trp/iata | dte energy co ~ dte (trp/iata); dte energy ~ dte (trp/iata) |
| DTE\|trp/iata | collision | Daet Airport | 4 | DTE | DTE | dte = fin/tck | dte ~ dte energy (fin/tck); dte ~ dte energy co (fin/tck) |
| GID\|trp/iata | control | Gitega Airport | 3 | GID | GID |  |  |
| LYB\|fin/tck | collision | LyondellBasell Industries N.V. | 5 |  |  |  |  |
| LYB\|trp/iata | collision | Edward Bodden Little Cayman Airfield | 5 | LYB | LYB |  |  |
| YGP\|trp/iata | control | Michel-Pouliot Gaspé Airport | 4 | YGP | YGP |  |  |
| MFG\|fin/tck | collision | MIZUHO FINANCIAL GROUP INC | 3 |  |  |  |  |
| MFG\|trp/iata | collision | Muzaffarabad Airport | 3 | MFG | MFG |  |  |
| WUS\|trp/iata | control | Nanping Wuyishan Airport | 6 | WUS | WUS |  |  |
| MHK\|fin/tck | collision | MOHAWK INDUSTRIES INC | 2 |  |  |  |  |
| HPP\|fin/tck | control | Hudson Pacific Properties, Inc. | 2 |  |  |  |  |
| MHK\|trp/iata | collision | Manhattan Regional Airport | 3 | MHK | MHK |  |  |
| OGL\|trp/iata | control | Eugene F. Correia International Airport | 3 | OGL | OGL |  |  |
| RKT\|fin/tck | collision | Rocket Companies, Inc. | 5 | RKT | RKT | rkt = trp/iata |  |
| RKT\|trp/iata | collision | Ras Al Khaimah International Airport | 3 | RKT | RKT | rkt = fin/tck |  |
| GYY\|trp/iata | control | Gary/Chicago International Airport | 3 | GYY | GYY |  |  |
| TCX\|trp/ica2 | collision | Thomas Cook Airlines | 5 | MT |  |  |  |
| EIA\|trp/ica2 | control | Evergreen International Airlines | 2 | EZ |  |  |  |
| TCX\|fin/tck | collision | TUCOWS INC /PA/ | 4 |  |  |  |  |
| TCX\|trp/iata | collision | Tabas Airport | 3 | TCX | TCX |  |  |
| XGR\|trp/iata | control | Kangiqsualujjuaq (Georges River) Airport | 5 | XGR | XGR |  |  |
| TPC\|fin/tck | collision | TUTOR PERINI CORP | 2 |  |  |  |  |
| TPC\|trp/ica2 | collision | Air Cal | 5 | TY |  |  |  |
| WMB\|fin/tck | collision | WILLIAMS COMPANIES, INC. | 3 |  |  |  |  |
| WMB\|trp/iata | collision | Warrnambool Airport | 3 | WMB | WMB |  |  |
| CXF\|trp/iata | control | Coldfoot Airport | 3 | CXF | CXF |  |  |
| AKY\|trp/ica2 | collision | Yak-Service | 3 | AKY | AKY | aky = trp/iata |  |
| VLK\|trp/ica2 | control | Vladivostok Air | 2 | XF |  |  |  |
| AKY\|trp/iata | collision | Sittwe Airport | 3 | AKY | AKY | aky = trp/ica2 |  |
| CBJ\|trp/iata | control | Cabo Rojo Airport | 3 | CBJ | CBJ |  |  |
| AXX\|trp/iata | collision | Angel Fire Airport | 1 |  |  |  |  |
| TOE\|trp/iata | control | Tozeur Nefta International Airport | 5 | TOE | TOE |  |  |
| AXX\|trp/ica2 | collision | Avioimpex A.D.p.o. | 5 | AXX, M4 | AXX |  |  |
| RMV\|trp/ica2 | control | Romavia | 1 |  |  |  |  |
| KAT\|trp/iata | collision | Kaitaia Airport | 3 | KAT | KAT |  |  |
| GVL\|trp/iata | control | Lee Gilmer Memorial Airport | 3 | GVL | GVL |  |  |
| KAT\|trp/ica2 | collision | Kato Airline | 2 |  |  |  |  |
| PSV\|trp/ica2 | control | Servicios Aereos Profesionales | 4 |  |  |  |  |
| PSD\|trp/iata | collision | Port Said International Airport | 5 | PSD | PSD |  |  |
| YPA\|trp/iata | control | Prince Albert Glass Field | 4 | YPA | YPA |  |  |
| PSD\|trp/ica2 | collision | President Airlines | 3 | TO |  |  |  |
| JEC\|trp/ica2 | control | Jett8 Airlines Cargo | 3 | JX |  |  |  |
| A\|fin/tck | collision | AGILENT TECHNOLOGIES, INC. | 3 |  |  |  |  |
| A\|cmp/dns | collision | a host address | 6 |  |  |  |  |
| SIG\|fin/tck | collision | SIGNET JEWELERS LTD | 5 |  |  |  |  |
| SIG\|trp/iata | collision | Fernando Luis Ribas Dominicci Airport | 4 | SIG | SIG |  |  |
| IFP\|trp/iata | control | Laughlin Bullhead International Airport | 6 | IFP | IFP |  |  |
| TXT\|fin/tck | collision | TEXTRON INC | 3 |  |  |  |  |
| TXT\|cmp/dns | collision | text strings | 4 |  |  |  |  |
