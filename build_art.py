"""Original, deterministic SVG artwork rendered into a competition-ready PNG.
The SVG is source material; main.py has no CairoSVG dependency.
"""
from pathlib import Path
import random
import cairosvg
from PIL import Image

HERE = Path(__file__).resolve().parent
random.seed(14077)

stars=[]
for i in range(170):
    x=random.randint(35,990); y=random.randint(28,950)
    if 170 < x < 866 and 250 < y < 850:
        continue
    r=random.choice([1.5,2.1,2.6,3.2]); alpha=random.choice([0.40,0.6,0.8,0.95])
    stars.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFF7D9" opacity="{alpha}"/>')

sparkles=[]
for x,y,s in [(121,180,10),(812,196,12),(897,414,13),(159,470,7),(805,710,9),(237,832,10),(944,759,7),(306,130,7)]:
    sparkles.append(f'<path d="M{x} {y-s*2} Q{x+s*0.22} {y-s*0.22} {x+s*2} {y} Q{x+s*0.22} {y+s*0.22} {x} {y+s*2} Q{x-s*0.22} {y+s*0.22} {x-s*2} {y} Q{x-s*0.22} {y-s*0.22} {x} {y-s*2}Z" fill="#FFF5B5" opacity=".9"/>')

svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
<defs>
 <radialGradient id="bg" cx="50%" cy="45%" r="80%"><stop stop-color="#384d8a"/><stop offset=".55" stop-color="#24365f"/><stop offset="1" stop-color="#141b39"/></radialGradient>
 <radialGradient id="light"><stop stop-color="#fffae7" stop-opacity=".58"/><stop offset=".38" stop-color="#ffefb8" stop-opacity=".19"/><stop offset="1" stop-color="#ffefb8" stop-opacity="0"/></radialGradient>
 <linearGradient id="mug" x1="0" y1="0" x2="0.1" y2="1"><stop stop-color="#fff4ee"/><stop offset=".54" stop-color="#f9d9dd"/><stop offset="1" stop-color="#eeb5cd"/></linearGradient>
 <linearGradient id="fox" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f9bc74"/><stop offset="1" stop-color="#de814e"/></linearGradient>
 <linearGradient id="blanket" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b4b4f8"/><stop offset="1" stop-color="#777ac2"/></linearGradient>
 <linearGradient id="nightCloud" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#778fbc" stop-opacity=".28"/><stop offset="1" stop-color="#8992cc" stop-opacity=".05"/></linearGradient>
</defs>
<rect width="1024" height="1024" fill="url(#bg)"/>
<circle cx="509" cy="392" r="408" fill="url(#light)"/>
{''.join(stars)}{''.join(sparkles)}
<!-- upper-left crescent -->
<circle cx="177" cy="192" r="58" fill="#FFEAB0" opacity=".95"/>
<circle cx="201" cy="168" r="58" fill="#273961"/>
<circle cx="155" cy="171" r="3.5" fill="#E7C88F" opacity=".7"/>
<!-- wispy background clouds -->
<g fill="url(#nightCloud)">
<ellipse cx="163" cy="715" rx="156" ry="37"/><ellipse cx="258" cy="713" rx="96" ry="23"/>
<ellipse cx="872" cy="585" rx="157" ry="35"/><ellipse cx="788" cy="585" rx="81" ry="19"/>
</g>
<!-- floor shadow and saucer -->
<ellipse cx="514" cy="856" rx="367" ry="45" fill="#101b3b" opacity=".55"/>
<ellipse cx="492" cy="831" rx="329" ry="43" fill="#f8d4db" stroke="#faeef1" stroke-width="12"/>
<ellipse cx="492" cy="832" rx="254" ry="23" fill="#e5a4c3" opacity=".4"/>
<!-- mug handle behind cup -->
<path d="M770 521 C896 508 930 578 902 666 C879 751 802 753 754 710" fill="none" stroke="#fcebf0" stroke-width="65" stroke-linecap="round"/>
<path d="M776 538 C866 532 900 588 869 661 C847 716 812 717 765 696" fill="none" stroke="#e4b2cb" stroke-width="13" stroke-linecap="round"/>
<!-- tails, warm soft characters peeking out from the mug -->
<path d="M367 593 C283 587 247 512 284 477 C320 441 359 467 361 485 C331 496 335 520 359 532 Q371 546 409 548" fill="url(#fox)" stroke="#c67856" stroke-width="8"/>
<path d="M282 481 C310 470 324 482 339 503 C328 512 330 524 346 535 C314 534 293 517 282 481Z" fill="#fff0dc"/>
<!-- cup dark tea surface -->
<ellipse cx="494" cy="563" rx="286" ry="77" fill="#c88ba3"/>
<ellipse cx="494" cy="553" rx="278" ry="64" fill="#ead1bb"/>
<ellipse cx="494" cy="553" rx="265" ry="52" fill="#b87a83" opacity=".42"/>
<!-- fox ears -->
<path d="M341 355 L336 242 Q338 215 358 232 L425 289Z" fill="#e69a61" stroke="#c97950" stroke-width="9"/>
<path d="M347 334 L348 266 L394 304Z" fill="#f3a7a3"/>
<path d="M545 298 L611 239 Q632 225 630 250 L616 365Z" fill="#e69a61" stroke="#c97950" stroke-width="9"/>
<path d="M569 307 L613 265 L603 341Z" fill="#f3a7a3"/>
<!-- fox head -->
<path d="M346 331 Q476 235 588 341 Q647 415 609 520 Q585 583 483 604 Q363 601 334 529 Q302 431 346 331Z" fill="url(#fox)" stroke="#c97950" stroke-width="8"/>
<!-- fox cheeks/central cream blaze -->
<path d="M401 464 Q425 416 477 444 Q532 413 572 466 Q610 525 558 554 Q503 587 471 567 Q428 582 391 546 Q362 516 401 464Z" fill="#fff2e5"/>
<!-- fox blushing cheeks -->
<ellipse cx="391" cy="475" rx="32" ry="17" fill="#e87670" opacity=".44"/>
<ellipse cx="559" cy="475" rx="32" ry="17" fill="#e87670" opacity=".44"/>
<!-- closed smile eyes -->
<g fill="none" stroke="#613d4c" stroke-width="9" stroke-linecap="round">
<path d="M380 444 Q415 467 443 441"/>
<path d="M512 441 Q542 464 578 439"/>
</g>
<!-- nose, tiny smile -->
<path d="M463 495 Q475 486 488 495 Q481 506 475 507Z" fill="#66435b"/>
<path d="M475 507 Q470 523 456 523 M475 507 Q478 523 493 522" fill="none" stroke="#66435b" stroke-width="5" stroke-linecap="round"/>
<!-- Bunny visible on the right -->
<ellipse cx="708" cy="387" rx="29" ry="110" transform="rotate(14 708 387)" fill="#f9e8e8" stroke="#e6c6d6" stroke-width="7"/>
<ellipse cx="760" cy="402" rx="29" ry="112" transform="rotate(28 760 402)" fill="#f9e8e8" stroke="#e6c6d6" stroke-width="7"/>
<ellipse cx="705" cy="381" rx="11" ry="74" transform="rotate(14 705 381)" fill="#f4baca"/>
<ellipse cx="760" cy="397" rx="11" ry="75" transform="rotate(28 760 397)" fill="#f4baca"/>
<ellipse cx="726" cy="508" rx="95" ry="92" fill="#f9e8e8" stroke="#e6c6d6" stroke-width="8"/>
<ellipse cx="686" cy="522" rx="14" ry="17" fill="#59465e"/><ellipse cx="767" cy="522" rx="14" ry="17" fill="#59465e"/>
<ellipse cx="686" cy="516" rx="5" ry="5" fill="white"/><ellipse cx="767" cy="516" rx="5" ry="5" fill="white"/>
<ellipse cx="668" cy="551" rx="23" ry="12" fill="#f0a7b8" opacity=".6"/>
<ellipse cx="783" cy="551" rx="23" ry="12" fill="#f0a7b8" opacity=".6"/>
<path d="M721 548 Q727 541 733 548 L727 554Z" fill="#aa7e8d"/>
<path d="M727 553 Q724 567 712 564 M727 553 Q734 569 744 564" fill="none" stroke="#a47688" stroke-width="4" stroke-linecap="round"/>
<!-- a tiny friendship heart in air -->
<path d="M636 283 C620 254 591 267 606 291 L639 320 L673 290 C686 262 653 251 636 283Z" fill="#ffbdc6" stroke="#ffeaec" stroke-width="5"/>
<circle cx="618" cy="285" r="4" fill="#fff8f0"/>
<!-- blanket draped over the sleepy fox and bunny -->
<path d="M247 581 C312 552 385 567 435 601 C489 560 556 576 616 586 C697 565 759 585 789 610 L762 722 Q702 816 504 819 Q291 816 239 714Z" fill="url(#blanket)" stroke="#f1e2fb" stroke-width="9"/>
<path d="M248 600 Q303 575 371 605 Q425 633 481 610 Q542 590 612 613 Q703 575 790 616" fill="none" stroke="#e9dffa" stroke-width="10" stroke-linecap="round"/>
<!-- tiny stars embroidered on blanket -->
<g stroke="#d8d9ff" stroke-width="5" stroke-linecap="round">
<path d="M350 664 V688 M338 676 H362"/><path d="M599 668 V688 M589 678 H609"/><path d="M482 715 V741 M470 728 H494"/>
</g>
<!-- little fox paws over blanket and bunny paw -->
<ellipse cx="393" cy="611" rx="33" ry="19" transform="rotate(10 393 611)" fill="#fff1e4" stroke="#d69f82" stroke-width="5"/>
<ellipse cx="557" cy="609" rx="33" ry="19" transform="rotate(-10 557 609)" fill="#fff1e4" stroke="#d69f82" stroke-width="5"/>
<ellipse cx="726" cy="620" rx="25" ry="18" fill="#fff0ef" stroke="#e6c6d6" stroke-width="5"/>
<!-- mug body painted OVER the blanket bottom -->
<path d="M214 632 C237 756 248 826 484 835 C725 833 758 752 778 632 Q736 665 665 667 C581 676 459 680 370 674 Q286 666 214 632Z" fill="url(#mug)" stroke="#fff4f1" stroke-width="13"/>
<!-- top edge -->
<path d="M208 629 Q493 730 783 628" fill="none" stroke="#fff8f5" stroke-width="21" stroke-linecap="round"/>
<path d="M222 656 Q495 731 766 654" fill="none" stroke="#e8a5c3" stroke-width="6" opacity=".75"/>
<!-- cup hand-drawn flower/heart -->
<circle cx="492" cy="746" r="60" fill="#fff4ed" opacity=".45"/>
<path d="M492 764 C462 745 438 728 452 705 C466 685 486 703 492 715 C505 689 525 687 539 706 C553 729 525 749 492 764Z" fill="#e88e9e" stroke="#f8f1e9" stroke-width="5"/>
<path d="M477 775 Q464 803 444 804 M505 778 Q524 797 544 802" fill="none" stroke="#72958a" stroke-width="7" stroke-linecap="round"/>
<path d="M461 797 Q448 775 429 789 Q443 807 461 797Z M524 795 Q548 772 560 790 Q544 809 524 795Z" fill="#84aaa3"/>
<!-- tiny warm steam shaped curls -->
<path d="M279 399 C241 366 285 337 271 309 M792 296 C811 269 792 251 812 225" stroke="#fff4de" stroke-opacity=".34" stroke-width="7" fill="none" stroke-linecap="round"/>
<!-- soft falling stars foreground -->
<circle cx="224" cy="381" r="5" fill="#fffbd0"/><circle cx="887" cy="288" r="6" fill="#fffbd0"/>
<!-- scarf-like dotted border for illustration book feel -->
<rect x="18" y="18" width="988" height="988" rx="56" fill="none" stroke="#f1d9c8" stroke-opacity=".37" stroke-width="4" stroke-dasharray="1 17" stroke-linecap="round"/>
</svg>'''
(HERE/'artwork.svg').write_text(svg,encoding='utf8')
cairosvg.svg2png(bytestring=svg.encode('utf8'),write_to=str(HERE/'entry.png'),output_width=1024,output_height=1024)
im=Image.open(HERE/'entry.png').convert('RGB')
im.save(HERE/'entry.png',format='PNG',optimize=True)
print('generated', HERE/'entry.png',(HERE/'entry.png').stat().st_size,'bytes')
