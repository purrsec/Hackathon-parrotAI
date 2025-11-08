import { z } from 'zod';

// Schéma pour getCoordonnees
export const getCoordonneesSchema = z.object({
  site_name: z.string().describe("Nom du site ou de la centrale à localiser"),
});

export type GetCoordonneesInput = z.infer<typeof getCoordonneesSchema>;

// Schéma pour getEtatInitial
export const getEtatInitialSchema = z.object({});

export type GetEtatInitialInput = z.infer<typeof getEtatInitialSchema>;

// Schéma pour getZoneInterdite
export const getZoneInterditeSchema = z.object({});

export type GetZoneInterditeInput = z.infer<typeof getZoneInterditeSchema>;

// Schéma pour planMissionRecon
export const planMissionReconSchema = z.object({
  lat: z.number().describe("Latitude de la cible"),
  lon: z.number().describe("Longitude de la cible"),
  radius_m: z.number().describe("Rayon de survol en mètres"),
  alt_m: z.number().describe("Altitude de survol en mètres"),
});

export type PlanMissionReconInput = z.infer<typeof planMissionReconSchema>;

// Schéma pour takeOff
export const takeOffSchema = z.object({
  alt_m: z.number().optional().describe("Altitude de décollage en mètres (optionnel)"),
});

export type TakeOffInput = z.infer<typeof takeOffSchema>;

// Schéma pour goTo
export const goToSchema = z.object({
  lat: z.number().describe("Latitude de destination"),
  lon: z.number().describe("Longitude de destination"),
  alt_m: z.number().describe("Altitude en mètres"),
  speed_mps: z.number().optional().describe("Vitesse en mètres par seconde (optionnel)"),
  orientation_mode: z.enum(["NONE", "TO_TARGET", "HEADING_START", "HEADING_DURING"]).optional().describe("Mode d'orientation: NONE (pas de changement), TO_TARGET (orienté vers la cible), HEADING_START (orientation avant départ), HEADING_DURING (orientation pendant le vol)"),
  heading: z.number().optional().describe("Cap en degrés (0-359, 0=Nord, 90=Est). Utilisé si orientation_mode est HEADING_START ou HEADING_DURING"),
});

export type GoToInput = z.infer<typeof goToSchema>;

// Schéma pour circle
export const circleSchema = z.object({
  target_lat: z.number().describe("Latitude de la cible"),
  target_lon: z.number().describe("Longitude de la cible"),
  alt_m: z.number().describe("Altitude en mètres"),
  radius_m: z.number().describe("Rayon de l'orbite en mètres"),
  laps: z.number().optional().describe("Nombre de tours (optionnel)"),
  direction: z.enum(["CW", "CCW", "default"]).optional().describe("Direction de l'orbite: CW (sens horaire), CCW (sens antihoraire), default (direction par défaut du drone)"),
});

export type CircleInput = z.infer<typeof circleSchema>;

// Schéma pour capture
export const captureSchema = z.object({
  type: z.enum(["photo", "video"]).describe("Type de capture: photo ou video"),
  duration_s: z.number().optional().describe("Durée en secondes pour une vidéo (optionnel)"),
});

export type CaptureInput = z.infer<typeof captureSchema>;

// Schéma pour returnToHome
export const returnToHomeSchema = z.object({});

export type ReturnToHomeInput = z.infer<typeof returnToHomeSchema>;

// Schéma pour land
export const landSchema = z.object({});

export type LandInput = z.infer<typeof landSchema>;

// Schéma pour getStatus
export const getStatusSchema = z.object({});

export type GetStatusInput = z.infer<typeof getStatusSchema>;

// Fonction helper pour convertir un schéma Zod en format JSON Schema pour MistralAI
export function zodToJsonSchema(schema: z.ZodObject<any>): any {
  const shape = schema.shape;
  const properties: any = {};
  const required: string[] = [];

  for (const [key, value] of Object.entries(shape)) {
    const zodType = value as z.ZodTypeAny;
    
    if (zodType instanceof z.ZodOptional) {
      properties[key] = zodToJsonSchemaType(zodType._def.innerType);
    } else {
      properties[key] = zodToJsonSchemaType(zodType);
      required.push(key);
    }
    
    // Ajouter la description si disponible
    if (zodType.description) {
      properties[key].description = zodType.description;
    }
  }

  return {
    type: "object",
    properties,
    required: required.length > 0 ? required : undefined,
  };
}

function zodToJsonSchemaType(zodType: z.ZodTypeAny): any {
  if (zodType instanceof z.ZodString) {
    return { type: "string" };
  }
  if (zodType instanceof z.ZodNumber) {
    return { type: "number" };
  }
  if (zodType instanceof z.ZodBoolean) {
    return { type: "boolean" };
  }
  if (zodType instanceof z.ZodEnum) {
    return { enum: zodType._def.values };
  }
  if (zodType instanceof z.ZodOptional) {
    return zodToJsonSchemaType(zodType._def.innerType);
  }
  if (zodType instanceof z.ZodObject) {
    return zodToJsonSchema(zodType);
  }
  return { type: "string" };
}

