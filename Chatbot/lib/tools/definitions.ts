import {
  getCoordonneesSchema,
  getEtatInitialSchema,
  getZoneInterditeSchema,
  planMissionReconSchema,
  takeOffSchema,
  goToSchema,
  circleSchema,
  captureSchema,
  returnToHomeSchema,
  landSchema,
  getStatusSchema,
  zodToJsonSchema,
} from './schemas';

// Définitions des outils pour MistralAI
export const toolDefinitions = [
  {
    type: "function" as const,
    function: {
      name: "getCoordonnees",
      description: "Résout le nom d'un site ou d'une centrale en coordonnées GPS (latitude, longitude)",
      parameters: zodToJsonSchema(getCoordonneesSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "getEtatInitial",
      description: "Récupère les paramètres par défaut du drone (point de retour, altitude de croisière, vitesse)",
      parameters: zodToJsonSchema(getEtatInitialSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "getZoneInterdite",
      description: "Récupère la liste des zones interdites (polygones) à éviter",
      parameters: zodToJsonSchema(getZoneInterditeSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "planMissionRecon",
      description: "Génère une planification de mission de reconnaissance avec des waypoints autour d'une cible. À appeler AUTOMATIQUEMENT pour chaque site après avoir récupéré ses coordonnées et l'état initial du drone. Utilise un rayon de 200m par défaut si non spécifié.",
      parameters: zodToJsonSchema(planMissionReconSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "takeOff",
      description: "Fait décoller le drone à l'altitude spécifiée (ou altitude par défaut si non spécifiée)",
      parameters: zodToJsonSchema(takeOffSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "goTo",
      description: "Envoie le drone à un point GPS spécifique (latitude, longitude, altitude)",
      parameters: zodToJsonSchema(goToSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "circle",
      description: "Fait effectuer au drone une orbite circulaire autour d'une cible. La direction peut être spécifiée: CW (sens horaire), CCW (sens antihoraire), ou default (direction par défaut du drone)",
      parameters: zodToJsonSchema(circleSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "capture",
      description: "Prend une photo ou lance l'enregistrement d'une vidéo",
      parameters: zodToJsonSchema(captureSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "returnToHome",
      description: "Fait retourner le drone au point de départ (home)",
      parameters: zodToJsonSchema(returnToHomeSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "land",
      description: "Fait atterrir le drone",
      parameters: zodToJsonSchema(landSchema),
    },
  },
  {
    type: "function" as const,
    function: {
      name: "getStatus",
      description: "Récupère l'état actuel du drone (état, batterie, position GPS, message)",
      parameters: zodToJsonSchema(getStatusSchema),
    },
  },
];

