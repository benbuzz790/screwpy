#Excerpt from NASA-TM-106943

## Fastener Axial Load

The total axial load in a fastener consists of the preload plus that portion of the external mechanical load not reacted by the joint. The total axial bolt load, $P_b$, can be given by (ref. 1):

$P_b = P_{b_{max}} + (SF × n\Phi P_{ext})$ (17)

where $P_{ext}$ is the resultant external force directed at the joint. This can be obtained through a free-body diagram of the system, finite element results, or other means. The external force must however include all components (e.g., prying action, moment resistance, etc.) that may increase or decrease the final force acting at the bolt. A factor of safety (SF) is applied to the external loading only (as opposed to $P_b$ as a whole) since the inaccuracies of the preloading process have already been accounted for. The amount of external load transferred to the bolt is dependent on the method of verification used (SF) and may differ from program to program. For flight-maturized, threaded applications the safety factors are normally 1.25 and 2.0 for yield and ultimate strength, respectively, while 1.1 and 1.4 are typical for nonpressurized, tested applications. Safety factors are strongly dependent on the specific application, method of loading, and overall design requirements, and therefore should be reviewed carefully before using them with the joint equations.

The terms n and Φ represent the effectiveness of the joint in inducing the amount of external loading transferred to the bolt. These parameters can be examined by considering the joint as a system of springs as shown in figure 4.

Under the initial preloading the bolt carries a tensile load while the flanges carry an equal compressive load. If an external tensile load, $P_{ext}$, is introduced very near the contact surface between the two flanges (n = 0), then the flanges are further compressed bringing almost their entire depth. Only a very small portion of the flanges between the indexing points is left without any significant relaxation of its compressive preload. At this spring diagram, acting as and d are very large in comparison to springs b and c. As the external load is applied, springs b and c are relieved (unloaded) of some of their compressive preload. The spring deflection ratio of springs b and c to a and d determines how much of the external loading is transferred to the bolt. As n gets greater, springs b and c get reduced in length (bolt remains at constant length between unloaded and loaded sections of the flanges). The section with the flanges reacts a large portion of the external loading as shown in fig (a).

When the magnitude of $P_{ext}$ reaches that of the initial preload $P_o$, all remaining compression in springs b and c has been relieved and the flange faces separate. Once the flanges have separated, the bolt is left to carry the entire external load.

If the external loading is applied at the free faces of the flanges (n = 1), the thickness of the flanges is relatively constant compared to loading is applied. All springs a, b, c, and d are relaxed. Since there is no flange material beyond the loading planes to undergo additional compression (such as in the previous case), the bolt elongates at the same rate as the flanges are relieved. In this situation the joint follows the load-deflection curve as shown in fig (b). Again, separation of the flanges is not encountered until all compression in the flanges has been relieved. For equal loading applied in both cases, the latter case (n = 1.0) results in greater load being transferred to the bolt.

In most practical joint applications the behavior of the joint is at some point between these two extremes. For common joint designs the load is carried somewhere near the midplanes of the flanges as shown in fig. With loading introduced near these midplanes (n = 0.5), the flange regions inboard and outboard of the loading planes work together much like the case of n = 0 but to a lesser degree. The loading plane factor is described by reference 1 as:

$n = \frac{\text{distance between loading planes}}{\text{total thickness of joint}}$ (18)

For most joints, it is usually acceptable to assume the loading planes to be located at the midplanes of the flanges or the midplanes outermost members if more than two components are being bolted. The joint configuration should always be examined closely to insure that this assumption is applicable.

The stiffness factor Φ determines the proportion in which the load is shared between bolt and joint. Since the extensional deflection, $δ_b$, of the bolt under an arbitrary tensile loading, $P_{ext}$, is equal to the amount of net deflection in the flanges, the force in each component can be determined with the aid of the load-deflection diagram (fig. 6):

$P_{ext} = ΔP_b + ΔP_j$ (19)

$ΔP_b = \left[\frac{P_{ext}}{δ_b + (1-n)δ_j}\right]δ$ (20)

$ΔP_j = \left(\frac{P_{ext}}{δ_j}\right)δ$ (21)

Rearranging equation (20) and using the result to rewrite equation (19) in terms of $ΔP_b$ give:

$δ = ΔP_b\left[\frac{δ_b + (1-n)δ_j}{P_{ext}}\right]$ (22)

$ΔP_j = \left(\frac{P_{ext}}{nδ_j}\right)ΔP_b\left[\frac{δ_b + (1-n)δ_j}{P_{ext}}\right] = ΔP_b\left[\frac{δ_b + (1-n)δ_j}{nδ_j}\right]$ (23)

$P_{ext} = ΔP_b + ΔP_j\left[\frac{δ_b + (1-n)δ_j}{nδ_j}\right] = ΔP_b\left[\frac{nδ_j + (δ_b + (1-n)δ_j)}{nδ_j}\right]$ (24)

$P_{ext} = ΔP_b\left(\frac{δ_b + δ_j}{nδ_j}\right)$ (25)

$δ_b = \frac{P_b}{K_b}$ (26)

$δ_j = \frac{P_j}{K_j} = δ_b\left(\frac{K_b}{K_j}\right)$ (27)

$P_{ext} = ΔP_b\left(\frac{K_b + K_j}{nK_b}\right)$ (28)

So the stiffness factor (or load factor) is defined as:

$\Phi = \frac{K_b}{K_b + K_j}$ (29)

Then equation (28) can be written as:

$ΔP_b = n\Phi P_{ext}$ (30)

The bolt stiffness, $K_b$, is equal to the axial stiffness of a circular rod with a cross section based on the nominal bolt diameter. The joint stiffness, $K_j$, is taken as the stiffness of the flange region which experiences the compressive preload. It can be very difficult to determine the exact region of the flange which is placed in compression and equally difficult to determine its stiffness. Several methods exist that estimate (either mathematically or experimentally) the stiffness of this load affected region; however, the method outlined by Shigley (ref. 6) has been used in this report. This method assumes the compressive loading in flanges(s) is distributed through 30° conical sections like those shown in fig. Relations for the various joint parameters are given for several typical joint configurations shown in figures 7 to 10.

## Configuration 1

Multiple parts are bolted together with a through-bolt and washer/nut combination. The bolt may be hex, socket, or pan head style (see fig. 7).

For configuration 1, the following equations apply:

$L = l_1 + l_2 + ... + l_n$ (31)

$K_b = \frac{AE_b}{L}$ (32)

$K_j = \frac{\pi E_j D}{2ln\left[\frac{L + 0.5D}{L + 2.5D}\right]}$ (33)

$\frac{L}{2l\pi E_j} = \left[\frac{l_1}{E_1} + \frac{l_2}{E_2} + ... + \frac{l_n}{E_n}\right]$ (34)

$n = \frac{l_1 + l_2 + ... + \frac{l_n}{2}}{l_1 + l_2 + ... + l_n}$ (35)

## Configuration 2

Parts are bolted together with a flat-head through-bolt and washer/nut combination (see fig. 8).

For configuration 2, the following equations apply:

$L = l_1 + l_2 + ... + (l_n - \frac{h}{2})$ (36)

$K_b = \frac{AE_b}{L}$ (37)

$K_j = \frac{\pi E_j D}{ln\left[\frac{(L + d_w - D)(d_w + D)(L + 0.5D)}{(L + d_w + D)(d_w - D)(L + 2.5D)}\right]}$ (38)

$d_w = \frac{d_h + D}{2}$ (39)

Note that if $d_w = 1.5D$, which is the case for typical aerospace fasteners, then equation (38) reduces to equation (33).

$E_j = \frac{L}{\sqrt{\frac{l_1}{E_1} + \frac{l_2}{E_2} + ... + \frac{l_n}{E_n}}}$ (40)

$n = \frac{(l_1 - \frac{h}{2}) + l_2 + ... + \frac{l_n}{2}}{l_1 + l_2 + ... + l_n}$ (41)

## Configuration 3

Parts are bolted together with a bolt threaded into the last part (with or without insert). The bolt may be hex, socket, or pan head style (see fig. 9).

For configuration 3, the following equations apply:

$L = l_1 + l_2 + ... + (l_n - \frac{L_1}{2})$ (42)

$K_b = \frac{AE_b}{L}$ (43)

$K_j = \frac{\pi E_j D}{ln\left[\frac{2.0L + 0.5D}{2.0L + 2.5D}\right]}$ (44)

$E_j = \frac{L}{\frac{l_1}{E_1} + \frac{l_2}{E_2} + ... + \frac{l_n - \frac{L_1}{2}}{E_n}}$ (45)

$n = \frac{l_1 + l_2 + ... + (l_n - \frac{L_1}{2})}{l_1 + l_2 + ... + l_n}$ (46)

## Configuration 4

Parts are bolted together using a flat-head bolt threaded into the last assembled part (see fig. 10).

For configuration 4, the following equations apply:

$L = (l_1 - \frac{h}{2}) + l_2 + ... + (l_n - \frac{L_1}{2})$ (47)

$K_b = \frac{AE_b}{L}$ (48)

$K_j = \frac{\pi E_j D}{ln\left[\frac{(L + d_w - D)(d_w + D)}{(L + d_w + D)(d_w - D)}\right]}$ (49)

$d_w = \frac{d_h + D}{2}$ (50)

Note again that, if $d_w = 1.5D$, then equation (49) reduces to equation (44).

$E_j = \frac{L}{\left(\frac{l_1 - \frac{h}{2}}{E_1}\right) + \frac{l_2}{E_2} + ... + \left(\frac{l_n - \frac{L_1}{2}}{E_n}\right)}$ (51)

$n = \frac{(l_1 - \frac{h}{2}) + l_2 + ... + (l_n - \frac{L_1}{2})}{l_1 + l_2 + ... + l_n}$ (52)
