---
sidebar_position: 2
title: "여기서 '언어'는 무엇을 의미하나요?"
---
# 여기서 무엇을 언어로 간주할까요?

> **핵심 요약.** Arena는 ISO 639-3에 따라 언어를 분류하고, (거대언어 우산 범주가 아닌) 개별 언어를 벤치마킹하며, 수어를 그 자체로 자연어로서 포함하고, ISO가 인정하는 인공어를 포함하며, 프로그래밍 언어는 제외하고, 분류학적 논쟁은 어느 한쪽 편을 들지 않고 표시해요. 이 페이지에서는 각 선택과 그것이 리더보드에 어떤 의미를 갖는지 설명해요.

수천 개의 언어에 걸쳐 번역을 벤치마킹하는 프로젝트라면 누구나 오래되고 놀라울 만큼 어려운 질문에 답해야 해요. 무엇을 언어로 간주할까요? 언어학자들은 "언어"와 "방언" 사이의 경계가 구조적인 만큼이나 사회적이고 정치적이라는 점을 오래전부터 알고 있었어요. *"언어란 육군과 해군을 가진 방언이다"*라는 유명한 경구는 1945년 이디시어 언어학자 Max Weinreich가 대중화한 것이에요(그는 자신의 강연 중 한 청중에게서 들었다고 밝혔어요). 이 질문을 피해 갈 수 없으니, 여기 우리의 답과 그 이유를 제시해요.

---

## 수어는 언어예요. 그게 전부예요.

수어는 완전한 문법, 아동에 의한 모어 습득, 살아 있는 언어 공동체를 갖춘 자연어예요. 이는 William Stokoe가 1960년에 미국 수어(American Sign Language)가 음성 언어와 같은 종류의 내부 구조를 갖는다는 것을 입증한 이래로 언어학에서 정립된 사실이며, 이후 60년간의 연구(Klima & Bellugi 1979; Sandler & Lillo-Martin 2006)는 이 점을 더욱 깊이 다질 뿐이었어요. ISO 639-3은 수어에 개별 언어 코드를 부여하며, Glottolog는 수어를 음성 언어 계통과 나란히 분류해요. 우리 카탈로그에는 `modality: signed`로 태그된 160개 이상의 수어가 포함되어 있어요.

일부는 멸종 위기에 처한 토착 언어예요. 역사적으로 북아메리카 전역에서 주요 부족 간 링구아 프랑카였던 평원 인디언 수어(Plains Indian Sign Language, `psd`)는 오늘날 심각한 멸종 위기에 처해 있어요(Davis 2010, *Hand Talk*). 수어의 위기는 *곧* 토착 언어의 위기이며, 이는 이 프로젝트의 사명 안에 있어요.

**솔직한 범위 설명.** Arena는 현재 *텍스트 기반* 기계 번역을 벤치마킹해요. 수어 MT는 영상, 공간 문법, 그리고 널리 채택된 문자 형식이 없는 언어를 다루는, 다르고 대체로 미해결인 기술적 문제예요(Yin et al. 2021, "Including Signed Languages in Natural Language Processing," ACL 참조). 우리는 아직 이를 지원하지 않아요. 우리 카탈로그의 수어 항목은 바로 그것을 말해요. **아직 지원되지 않음 — 결코 "언어가 아님"이 아니에요.**

## 양식은 두 가지예요. 문자는 그중 하나가 아니에요.

언어는 두 가지 주요 양식으로 나타나요. **음성**과 **수어**예요. 문자는 세 번째 양식이 아니에요. 그것은 언어 위에 얹힌 기술이며, 세계 대부분의 언어는 표준화된 문자 없이도 잘 지내요. 그래서 우리 언어 카드는 문자를 별도로 추적하며(어떤 언어가 어떤 문자를 사용하는지, 또는 표준화된 정서법이 전혀 없는지), 이를 솔직하게 추적해요. 텍스트 기반 MT 플랫폼에서 어떤 언어가 문자를 가졌는지는 각주가 아니라 결정적인 정보예요. 그리고 문자가 없는 언어가 열등한 언어인 것은 아니에요.

## 인공어는 포함, 프로그래밍 언어는 제외예요.

우리는 ISO 639-3 자체의 기준을 따라요. 이 표준은 인공어가 완전한 언어이고, 인간의 의사소통을 위해 설계되었으며, 문헌이 있고, 이를 2세대 사용자에게 전수한 공동체가 있을 경우에만 인공어를 인정하며, 컴퓨터 프로그래밍 언어는 명시적으로 제외해요. 모어 화자가 있는 Esperanto는 자격을 갖추지만, Python은 그렇지 않아요. 누구도 Python을 부모에게서 제1언어로 습득하지 않기 때문이에요. 우리 카탈로그에는 ISO가 인정하는 24개의 인공어가 그에 맞게 유형이 지정되어 포함되어 있으며, 프로그래밍 언어는 없어요.

## 우리는 우산 범주가 아니라 개별 언어를 벤치마킹해요

ISO 639-3은 *개별 언어*와 *거대언어(macrolanguage)*를 구분해요. 거대언어는 `cre`(Cree), `ara`(Arabic), `zho`(Chinese)처럼 밀접하게 관련된 여러 개별 언어를 포괄하는 우산 코드예요. Arena의 벤치마크 단위는 **개별 언어**이며, 그 이유는 실무적이에요. 번역 자원은 변종마다 고유하기 때문이에요. 평원 크리어(Plains Cree, `crk`)를 위해 만든 형태소 분석기는 무스 크리어(Moose Cree, `crm`)를 생성하지 못해요. 이집트 아랍어 말뭉치는 모로코 아랍어에서 어떤 방법의 품질에 대해 거의 알려주는 바가 없어요. 우산 코드에 붙은 점수는 실제로 평가된 적 없는 변종에 대한 주장이 될 테니, 우리는 그렇게 하지 않아요.

거대언어는 여전히 카탈로그에 **허브 페이지**로 나타나요. 우산 정체성을 그 개별 구성원과 연결하는 내비게이션으로, 두 층위의 정체성 모두 실재한다는 ISO 자체의 관찰을 반영해요. 개별 언어 아래에서는 Glottolog의 언어소(languoid) 트리(Hammarström & Forkel 2022)에서 가져온 방언 및 계통 정보를 표시하는데, 이 트리는 계통, 언어, 방언을 하나의 탐색 가능한 위계로 모델링해요.

## 권위 있는 출처들이 의견을 달리할 때, 우리는 둘 다 보여줘요

ISO 639-3과 Glottolog는 때때로 다르게 나누거나 묶으며, 공동체가 둘 모두와 의견을 달리하기도 해요. 우리는 판결하지 않아요. 언어 카드에는 그 불일치를 출처와 함께 표시하는 *분류학 주석* 기능이 담겨 있으며, 공동체가 선호를 표명한 경우에는 어디서나 그 명명을 따라요. 어떤 변종이 "하나의 언어"인지는 결국 부분적으로 정체성의 문제이며, 정체성 문제는 공동체 자신에게 속해요. 이는 OCAP®과 같은 토착 데이터 거버넌스 프레임워크에서 채택한 원칙이에요.

## 연구 방향: 측정 도구로서의 벤치마크

이와 같은 아레나가 거의 부산물로 만들어내는 한 가지는 언어 변종들이 *실무적으로* 실제로 얼마나 가까운지에 대한 새로운 종류의 증거예요. 고정된 하나의 번역 방법이 여러 관련 변종을 배포 가능한 품질로 처리한다면, 그 변종들은 실무적으로 군집을 이뤄요. 별도의 말뭉치와 별도의 방법을 요구한다면, 그것들은 명명 정치가 뭐라고 하든 실무적으로 구별되는 것이에요. 이는 녹음 텍스트 이해도 검사부터 자동화된 어휘 거리 측정에 이르기까지 오래된 경험적 전통과 닮았지만, 배포에 기반한 변형을 더했어요.

우리는 이를 주장이 아니라 연구 방향으로서 신중하게 제시해요. 방법 전이 결과는 말뭉치 규모, 도메인, 정서법, 훈련 데이터 오염에 의해 교란되며, 군집화는 언제나 특정 방법과 품질 임계값에 상대적이에요. 무엇보다도, 이 신호는 언어와 방언에 관한 대화에 *정보를 제공*할 수는 있지만, 공동체가 자신의 언어를 어떻게 정체화하는지를 결코 뒤엎지 못해요.

---

## 참고 문헌

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