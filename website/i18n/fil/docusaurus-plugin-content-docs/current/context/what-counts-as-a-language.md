---
sidebar_position: 2
title: "Ano ang Itinuturing na Wika Dito?"
---
# Ano ang Maituturing na Wika Dito?

> **Buod para sa mga Tagapagpasiya.** Kinakatalogo ng Arena ang mga wika ayon sa ISO 639-3, nagbe-benchmark ng mga indibidwal na wika (hindi mga payong na macrolanguage), isinasama ang mga wikang pasenyas bilang mga natural na wikang tunay na sila, isinasama ang mga constructed language na kinikilala ng ISO, ibinubukod ang mga programming language, at ipinapakita ang mga pagtatalo sa taxonomy nang hindi kumakampi. Ipinapaliwanag ng pahinang ito ang bawat pasiya at kung ano ang kahulugan nito para sa leaderboard.

Ang anumang proyektong nagbe-benchmark ng pagsasalin sa libo-libong wika ay kailangang sumagot sa isang luma at nakakagulat na mahirap na tanong: ano ang maituturing na wika? Matagal nang alam ng mga lingguwista na ang hangganan sa pagitan ng "wika" at "diyalekto" ay kasing-sosyal at kasing-politikal ng pagiging estruktural nito — ang bantog na biro na *"ang wika ay isang diyalektong may hukbo at hukbong-dagat"* ay pinasikat ng lingguwistang Yiddish na si Max Weinreich noong 1945 (ipinagkredito niya ito sa isang tagapakinig sa isa sa kaniyang mga lektura). Hindi po namin maiiwasan ang tanong, kaya narito ang aming mga sagot, at ang aming pangangatwiran.

---

## Ang mga wikang pasenyas ay mga wika. Tuldok.

Ang mga wikang pasenyas ay mga natural na wika — may kumpletong gramatika, likas na pagtatamo ng mga bata, at buhay na mga komunidad ng wika. Matagal na itong napagtibay sa lingguwistika mula noong ipinakita ni William Stokoe noong 1960 na ang American Sign Language ay may parehong uri ng panloob na estruktura gaya ng mga wikang sinasalita, at lalo lamang itong pinatibay ng animnapung taon ng pananaliksik mula noon (Klima & Bellugi 1979; Sandler & Lillo-Martin 2006). Naglalaan ang ISO 639-3 ng mga indibidwal na code ng wika sa mga wikang pasenyas; kinakatalogo sila ng Glottolog kasabay ng mga pamilyang sinasalita. Kabilang sa aming katalogo ang higit sa 160 sa mga ito, na may tag na `modality: signed`.

Ang ilan ay nanganganib na mga Indigenous language: ang Plains Indian Sign Language (`psd`), na sa kasaysayan ay isang pangunahing intertribal lingua franca sa buong North America, ay kritikal na nanganganib sa kasalukuyan (Davis 2010, *Hand Talk*). Ang pagkapanganib ng wikang pasenyas *ay* pagkapanganib ng Indigenous language, at saklaw ito ng misyon ng proyektong ito.

**Isang tapat na tala sa saklaw.** Sa kasalukuyan, nagbe-benchmark ang Arena ng *text-based* machine translation. Ang signed-language MT — na gumagana sa video, spatial grammar, at mga wikang walang malawakang tinatanggap na nakasulat na anyo — ay ibang teknikal na suliranin at higit na hindi pa nalulutas (tingnan ang Yin et al. 2021, "Including Signed Languages in Natural Language Processing," ACL). Hindi pa namin ito naihahain. Eksaktong sinasabi iyon ng mga entry ng wikang pasenyas sa aming katalogo: **hindi pa naihahain — kailanman ay hindi "hindi isang wika."**

## May dalawang modalidad. Hindi isa rito ang pagsulat.

May dalawang pangunahing modalidad ang mga wika: **sinasalita** at **pinapasen­yas**. Ang pagsulat ay hindi ikatlong modalidad — ito ay teknolohiyang ipinapatong sa isang wika, at karamihan sa mga wika sa mundo ay nakagagamit nang walang estandardisadong anyo nito. Kaya naman hiwalay na sinusubaybayan ng aming mga language card ang pagsulat (kung aling mga script ang ginagamit ng isang wika, o kung wala ba itong estandardisadong ortograpiya sa lahat) at tapat namin itong sinusubaybayan: para sa isang text-based MT platform, kritikal na impormasyon kung naisusulat ba ang isang wika, hindi isang talababa — at ang wikang hindi naisusulat ay hindi mas mababang uri ng wika.

## Constructed languages: kasama. Programming languages: hindi kasama.

Sinusunod namin ang sariling linya ng ISO 639-3. Tinatanggap lamang ng pamantayan ang isang constructed language kung ito ay isang kumpletong wika, dinisenyo para sa komunikasyon ng tao, may panitikan at komunidad na naipasa ito sa ikalawang henerasyon ng mga gumagamit — at tahasan nitong ibinubukod ang mga computer programming language. Kwalipikado ang Esperanto, dahil mayroon itong mga native speaker; hindi kwalipikado ang Python, dahil walang nagtatamo ng Python bilang unang wika mula sa kanilang mga magulang. Kabilang sa aming katalogo ang dalawang dosenang constructed language na kinikilala ng ISO, na nakatukoy bilang ganoon, at walang programming language.

## Nagbe-benchmark kami ng mga indibidwal na wika, hindi mga payong

Tinutukoy ng ISO 639-3 ang pagkakaiba ng *mga indibidwal na wika* at *mga macrolanguage* — mga payong na code gaya ng `cre` (Cree), `ara` (Arabic), o `zho` (Chinese) na sumasaklaw sa ilang magkakaugnay na indibidwal na wika. Ang yunit ng benchmark ng Arena ay ang **indibidwal na wika**, dahil sa isang operasyonal na dahilan: espesipiko sa variety ang mga resource sa pagsasalin. Ang morphological analyzer na binuo para sa Plains Cree (`crk`) ay hindi bumubuo ng Moose Cree (`crm`); ang corpus ng Egyptian Arabic ay kaunti ang masasabi tungkol sa kalidad ng isang method sa Moroccan Arabic. Ang score na nakakabit sa isang payong na code ay magiging isang pahayag tungkol sa mga variety na hindi naman aktuwal na nasuri — kaya hindi namin ito ginagawa.

Lumilitaw pa rin ang mga macrolanguage sa katalogo bilang **mga hub page**: nabigasyon na nag-uugnay ng isang payong na identidad sa mga indibidwal nitong kasapi, bilang pagsasalamin sa sariling obserbasyon ng ISO na totoong umiiral ang parehong antas ng identidad. Sa ibaba ng indibidwal na wika, ipinapakita namin ang impormasyon sa diyalekto at lineage mula sa languoid tree ng Glottolog (Hammarström & Forkel 2022), na nagmomodelo ng mga pamilya, wika, at diyalekto bilang isang nabigableng hierarchy.

## Kapag hindi nagkakasundo ang mga awtoridad, ipinapakita namin ang pareho

Paminsan-minsan, magkaiba ang paghihiwalay o pagsasama ng ISO 639-3 at Glottolog, at minsan ay hindi rin sang-ayon ang mga komunidad sa pareho. Hindi kami humahatol. Ang mga language card ay may affordance na *mga tala sa taxonomy* na nagpapakita ng hindi pagkakasundo kasama ang mga sanggunian, at sumusunod ang pagpapangalan sa komunidad saanman nagpahayag ng kagustuhan ang komunidad. Kung ang isang variety ay "isang wika" ay, sa huli, bahagyang tanong ng identidad — at ang mga tanong ng identidad ay nabibilang sa mismong mga komunidad, isang prinsipyong hinango namin mula sa mga Indigenous data-governance framework gaya ng OCAP®.

## Isang direksiyon ng pananaliksik: ang mga benchmark bilang instrumentong pansukat

Ang isang bagay na nalilikha ng isang arena na tulad nito, halos bilang by-product, ay isang bagong uri ng ebidensiya tungkol sa kung gaano talaga kalapit ang mga variety ng wika sa *operasyonal* na paraan. Kung ang isang iisang method ng pagsasalin, na pinananatiling hindi nagbabago, ay nakapaglilingkod sa ilang magkakaugnay na variety sa kalidad na maaaring i-deploy, nagku-cluster ang mga variety na iyon sa praktika; kung nangangailangan sila ng magkakahiwalay na corpus at magkakahiwalay na method, operasyonal silang magkakaiba — anuman ang sabihin ng politika ng pagpapangalan. Kahawig ito ng mas matatandang empirikal na tradisyon, mula sa recorded-text intelligibility testing hanggang sa mga automated lexical-distance measure, ngunit may paglikong nakaugat sa deployment.

Inilalahad po namin ito nang maingat, bilang direksiyon ng pananaliksik sa halip na isang pahayag. Ang mga resulta ng method-transfer ay napagugulo ng laki ng corpus, domain, ortograpiya, at kontaminasyon ng training-data, at ang clustering ay palaging relatibo sa isang method at threshold ng kalidad. Higit sa lahat: maaaring *magbigay-kaalaman* ang signal na ito sa mga pag-uusap tungkol sa wika at diyalekto, ngunit hindi nito kailanman pinapalitan ang paraan ng pagtukoy ng isang komunidad sa sarili nitong wika.

---

## Mga Sanggunian

- Davis, Jeffrey E. (2010). *Hand Talk: Sign Language among American Indian Nations.* Cambridge University Press.
- Dryer, Matthew S. & Martin Haspelmath, eds. (2013). *The World Atlas of Language Structures Online.* https://wals.info
- Hammarström, Harald & Robert Forkel (2022). "Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information." *Semantic Web* 13(6).
- Haugen, Einar (1966). "Dialect, Language, Nation." *American Anthropologist* 68(4).
- ISO 639-3 Registration Authority. "Scope of denotation" and "Types of individual languages." https://iso639-3.sil.org/about/scope · https://iso639-3.sil.org/about/types
- Klima, Edward S. & Ursula Bellugi (1979). *The Signs of Language.* Harvard University Press.
- Sandler, Wendy & Diane Lillo-Martin (2006). *Sign Language and Linguistic Universals.* Cambridge University Press.
- Stokoe, William C. (1960). *Sign Language Structure.* Studies in Linguistics, Occasional Papers 8.
- Weinreich, Max (1945). "Der YIVO un di problemen fun undzer tsayt." *YIVO Bleter* 25(1).
- Yin, Kayo, Amit Moryossef, Julie Hochgesang, Yoav Goldberg & Malihe Alikhani (2021). "Including Signed Languages in Natural Language Processing." *Proc. ACL-IJCNLP 2021.* https://aclanthology.org/2021.acl-long.570/
- First Nations Information Governance Centre. *The First Nations Principles of OCAP®.* https://fnigc.ca/ocap-training/