EC01 – La solution doit permettre de déclarer manuellement des écarts dans une base de données unique
La solution de gestion des écarts doit permettre la déclaration d’un écart, via un formulaire proposant différents champs. 
Une fois le formulaire validé, une nouvelle entrée sera créée dans une base de données unique contenant tous les écarts déclarés.
OK

EC02 – La solution doit permettre de lier un écart à un audit existant
Lors de la création d’un écart, qu’elle ait lieu lors de la réalisation d’un audit/dialogue ou ultérieurement, l’utilisateur doit être en mesure de lier l’écart à un audit existant.
Ok : on peut le relier indiquand la source de l'audit / une référence / une pièce jointe à la déclaration

EC03 – La solution doit permettre de préremplir des champs en fonction des informations saisies dans la déclaration d'audit
Lors de la création d’un écart, les champs liés à l’audit lui-même doivent se remplir automatiquement.
NOK 

EC04 – La solution doit permettre de saisir plusieurs écarts, sans re-saisie des champs liés à l'audit
Une déclaration d’écart est composée de deux parties :
- Un en-tête, contenant des informations générales liées à l’audit
- Une deuxième partie, contenant les informations propres à l’écart.
OK

EC05 – La solution doit permettre de modifier un écart après saisie. Une fois un écart enregistré, il doit être possible de le modifier et l’enregistrer, sans que cela ne créer une nouvelle entrée dans la base de données.
OK mais seulement d'admin et le déclarant peuvent les modifier 

EC07 – La solution doit fournir un suivi des modifications des écarts. La solution doit proposer un système d’historisation des modifications apportées à l’écart. Ce système doit permettre d’obtenir le nom de l’auteur, la date et la
nature de la modification.
A FAIRE

EC06 – La solution doit permettre de supprimer un écart après saisie. Une fois un écart enregistré, il doit être possible de le supprimer de la base de données.
OK le déclarant peut modifier le statut d'un écart en annulé (dans ce cas ils n'apparaissent plus que pour lui et les admin) / les administrateurs peuvent supprimer les écart des la bdd 

EC08 – La solution doit proposer une corbeille des écarts supprimés La solution doit proposer un système de rétention temporaire des écarts supprimés, permettant leur restauration durant un certain laps de temps.
NOK il n'y a pas de corbeille mais seulement une liste d'écart annuler accéssible par les admin

EC09 – La solution doit permettre la notification d'un utilisateur lorsqu'un écart est supprimé
La solution doit permettre la notification d’un ou plusieurs utilisateurs lorsqu’un écart est supprimé.
A FAIRE

EC10 – La solution doit permettre de créer des champs dont les valeurs sont prédéfinies
Le formulaire de déclaration d’un écart doit pouvoir contenir des champs dont les valeurs sont prédéfinies par l’administrateur de l’outil, via une liste déroulante, un menu à choix multiple, ou une autre solution similaire.
OK


EC11 – La référence de la source doit être un menu déroulant présentant tous les ID d’audit disponibles pour un type d'audit donné
Dans le formulaire de déclaration d’un écart, le champs « référence de la source » contient l’identifiant de l’audit auquel l’écart est lié. Cette référence doit être choisie dans une liste proposant tous les identifiants existant pour un type d’audit donné. Les valeurs de cette liste sont donc automatiquement mises à jour si le
champ « comment » est modifié. Exemple : Un utilisateur souhaite saisir un écart lié à un audit interne. Lorsqu’il va indiquer « audit interne » dans le champ « comment », le champ « référence de la source » lui listera les identifiants de tous les audits internes existant.
NOK

EC12 – La solution doit permettre de créer des champs dont les valeurs sont des dates
Dans le formulaire de déclaration d’un écart, il doit être possible de remplir un champ contenant une date. Cette date doit être formatée de la même manière pour tous les écarts enregistrés dans la base de données.
OK

EC13 – La solution doit permettre de créer des champs dont les valeurs sont récupérées dans l'annuaire Enercal
Dans le formulaire de déclaration d’un écart, il doit être possible de créer des champs dans lesquels l’utilisateur peut déclarer le nom d’une personne présente dans l’annuaire Enercal. Ce champ permet la vérification de l’orthographe du
nom de la personne. Il doit être formaté de la même manière pour tous les écarts enregistrés dans la base de données.
NOK, l'annuaire est a réimporter dans l'admin

EC14 – La solution doit permettre de créer des champs dont les valeurs sont saisies manuellement par l'utilisateur
Dans le formulaire de déclaration d’un écart, il doit être possible de créer des champs dans lesquels l’utilisateur peut saisir du texte libre.
OK

EC15 – Le détail de l'écart doit être une liste dont les valeurs varient en fonction du
champ comment
Dans le formulaire de déclaration d’un écart, le détail de l’audit (champ « quoi »)
doit être une liste préfinie dont les valeurs dépendent de la source de l’écart
(champ « comment »).
OK


EC16 – L’état d'un écart doit se mettre automatiquement à jour lorsque toutes les actions liées à l'écart sont clôturées
Suite à une déclaration d’écart, une ou plusieurs actions peuvent être créées dans le plan d’action unique (voir chapitre Plan d’action unique ).
Dans le formulaire de déclaration d’un écart, le champ « état » d’un écart doit se mettre automatiquement à jour lorsque toutes les actions liées à cet écart ont été réalisées.
A FAIRE

EC17 – La solution doit permettre l'ajout de plusieurs pièces jointes à chaque écart
La solution doit permettre d’intégrer une ou plusieurs pièces jointes à chaque
déclaration d’écart.
OK

2.2. Workflow de validation d’un écart
Une fois l’écart créé, il doit être validé par un ou plusieurs responsables. Un
workflow permet l’automation des différentes étapes de validation de l’écart.

WF01 – La solution doit permettre de déterminer automatiquement les responsables
de l&#39;écart
La solution doit permettre de déterminer automatiquement une matrice des
responsables d’un écart, en fonction du type de source de l’écart (champ
« comment »), de l’unité et/ou du service concerné (champ « où »), et du
processus.
Chaque écart peut posséder jusqu’à trois niveaux de responsables. Ces derniers
sont décrits dans les documents du dossier « matrice de validation des écarts ».

WF02 – Les utilisateurs finaux sont autonomes pour mettre à jour la matrice des
responsables d&#39;écarts
Afin de gérer les absences des responsables, un groupe d’utilisateurs définis par
l’administrateur de la solution doit pouvoir mettre à jour la matrice des
responsables d’écart.

12
SMI 2.0 – Gestion des écarts – Cahier des charges
WF03 – Lorsqu&#39;un écart est enregistré, le responsable de premier niveau doit être
automatiquement sollicité pour validation de l&#39;écart
Lorsqu’un écart est enregistré dans la base de données, le responsable de
premier niveau doit en être automatiquement informé, et doit pouvoir valider ou
refuser l’écart.

WF04 – La solution doit permettre la notification du responsable de niveau supérieur
lorsqu&#39;un responsable valide l&#39;écart
Lorsqu’un écart est validé par un responsable, le responsable de niveau supérieur
en est notifié, et doit à son tour valider ou refuser l’écart.
Dans le cas où l’écart est refusé par un responsable, le responsable de niveau
supérieur n’est ni notifié, ni sollicité pour validation.

WF05 – Le statut de l&#39;écart est automatiquement mis à jour par le workflow
Le statut de l’écart doit être automatiquement mis à jour dans les cas suivants :
- Un responsable refuse un écart,
- Tous les responsables ont validé l’écart.

WF06 – Lors du changement automatique de statut d&#39;un écart, le créateur de l&#39;écart
doit en être notifié
Lorsque le workflow met automatiquement à jour le statut d’un écart, le créateur
de ce dernier doit en être notifié.

WF07 – Lors du changement automatique de statut d&#39;un écart, un groupe d’utilisateur
défini doit en être notifié
Lorsque le workflow configure automatiquement le statut d’un écart à « retenu »,
un groupe d’utilisateur doit en être notifié. Ce groupe est défini en fonction du
type d’audit source (champ « comment »).

2.3. Plan d’action unique
AC01 – La solution doit permettre de déclarer des actions

13
SMI 2.0 – Gestion des écarts – Cahier des charges
Chaque déclaration d’écart peut engendrer zéro, une ou plusieurs actions. Ces
actions doivent être déclarées via un formulaire, et stockées dans une base de
données unique, permettant une visualisation centralisée de toutes les actions à
traiter.
Les différents champs d’une action sont les suivants :
 Description de l&#39;action 
 Identifiant de l&#39;écart lié 
 Affecté à
 Contributeurs (une ou plusieurs personnes)
 Date d&#39;échéance initiale 
 Nouvelle date d&#39;échéance 
 Priorité (urgent, important…)
 Statut (en cours, non réalisée mais clôturer, terminée)
 Commentaires
 Site
 PJ 

AC02 – Il n&#39;est pas possible de déclarer une action qui ne soit pas liée à un écart
Chaque action est obligatoirement liée à un écart. La solution doit donc
empêcher la création d’une action non liée à un écart.

AC03 – L’écart auquel l’action est rattachée est identifié dans l’action
Le formulaire de déclaration d’une action possède un champ permettant
l’identification de l’écart associé.

AC04 – Seuls les écarts validés peuvent engendrer des actions
Les écarts &quot;déclarés&quot; et &quot;non retenus&quot; ne doivent pas pouvoir engendrer d&#39;actions.

AC05 – Il doit être possible de récupérer la source d&#39;écart associée à l&#39;action
Il doit être possible d’identifier à quel type d’audit une action est associée (audit
interne, AFNOR…).

AC06 – Une action ne peut être affectée qu&#39;à une seule personne

14
SMI 2.0 – Gestion des écarts – Cahier des charges
Le formulaire de déclaration d’une action doit permettre d’affecter cette dernière
à une personne, sélectionnée dans l’annuaire Enercal. Il ne doit pas être possible
d’affecter une tâche à plusieurs personnes.

AC07 – La solution doit permettre de créer des champs dont les valeurs sont
prédéfinies
Le formulaire de déclaration d’une action doit pouvoir contenir des champs dont
les valeurs sont prédéfinies par l’administrateur de l’outil, via une liste déroulante,
un menu à choix multiple, ou une autre solution similaire.

AC08 – La solution doit permettre de créer des champs dont les valeurs sont des
dates
Dans le formulaire de déclaration d’une action, il doit être possible de remplir un
champ contenant une date. Cette date doit être formatée de la même manière
pour toutes les actions enregistrées dans la base de données.

AC09 – La solution doit permettre d’ajouter un ou plusieurs commentaires à une
action
Dans le formulaire de déclaration d’une action, il doit être possible de renseigner
un commentaire concernant l’action. L’ajout de commentaire doit pouvoir être
également effectué après l’enregistrement de l’action.

AC10 – La solution doit fournir un suivi des modifications des actions
La solution doit proposer un système d’historisation des modifications apportées
à l’action. Ce système doit permettre d’obtenir le nom de l’auteur, la date et la
nature de la modification.

AC11 – La solution doit empêcher la modification de certains champs de l&#39;action une
fois celle-ci créée
Une fois une action enregistrée, certains champs ne doivent plus pouvoir être
modifiés. Les seuls champs modifiables après enregistrement sont « affecté à »,
« contributeurs », « nouvelle date d’échéance », « statut », ainsi que l’ajout de
commentaire et de pièces jointes.

15
SMI 2.0 – Gestion des écarts – Cahier des charges
AC12 – La solution doit permettre de dupliquer une action, en conservant les données
déjà remplies
Un utilisateur doit pouvoir dupliquer une action existante, ce qui aura pour effet
de créer une nouvelle action contenant strictement les mêmes informations que
l’action source.

AC13 – La solution doit permettre l&#39;intégration d&#39;une URL dans l&#39;action
Le formulaire de déclaration d’une action doit permettre l’insertion d’un lien, soit
lors de la déclaration initiale, soit à postériori.

AC14 – La création d&#39;une action engendre des notifications contenant un lien
permettant de consulter l&#39;action
Lors de la création d’une action, les personnes spécifiées dans les champs
« affecté à » et « contributeurs » doivent recevoir une notification contenant un
lien vers l’action.

AC15 – La modification de certains champs entraine des notifications
Après l’enregistrement d’une action en base de données, lorsque les champs
« affecté à » et « contributeurs » sont modifiés, les personnes spécifiées dans ces
champs en sont notifiées.

AC16 – La solution doit permettre l&#39;envoi de notifications récurrentes à chaque
utilisateur, récapitulant les tâches qui lui sont assignées
La solution doit permettre l’envoi de notifications récurrentes (par exemple, tous
les lundis matin), dans lesquelles l’utilisateur retrouve la liste de toutes les tâches
qui lui sont assignées.

AC17 – Il doit être possible de filtrer et trier l&#39;affichage des actions
Il doit être possible de trier et filtrer l’affichage des différentes actions, en fonction
de plusieurs critères liés à l’action elle-même, à l’écart lié, ou au type d’audit ayant
produit l’action.

2.4. Exigences non fonctionnelles

16
SMI 2.0 – Gestion des écarts – Cahier des charges
NF01 – L&#39;administrateur de la solution doit pouvoir modifier les valeurs des champs
dont les valeurs sont prédéfinies
L’administrateur de la solution doit pouvoir modifier les différents champs dont
les valeurs sont prédéfinies (listes déroulantes…).

NF02 – Les identifiants utilisés pour la connexion doivent être les comptes Active
Directory des utilisateurs

NF03 – Enercal doit être autonome pour maintenir la solution
Les équipes Enercal doivent pouvoir être autonomes pour le maintien de la
solution, et ne doivent pas avoir besoin de faire appel à des prestataires externes.

NF04 – Il devra être possible d&#39;exploiter les données des bases de données sous
PowerBI
Les données générées par chacune des bases de données doivent pouvoir être
exploitables sous PowerBI.