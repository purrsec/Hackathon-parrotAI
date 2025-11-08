import axios from 'axios';
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
} from './schemas';

const DRONE_API_URL = process.env.DRONE_API_URL || 'http://localhost:8000';

// Base de données simple pour les coordonnées (à remplacer par une vraie DB)
const sitesDatabase: Record<string, { lat: number; lon: number }> = {
  'centrale nucléaire de fessenheim': { lat: 47.9094, lon: 7.5603 },
  'centrale de fessenheim': { lat: 47.9094, lon: 7.5603 },
  'fessenheim': { lat: 47.9094, lon: 7.5603 },
  'centrale nucléaire de cattenom': { lat: 49.4144, lon: 6.2131 },
  'cattenom': { lat: 49.4144, lon: 6.2131 },
  'centrale de cattenom': { lat: 49.4144, lon: 6.2131 },
  'centrale nucléaire de gravelines': { lat: 51.01666, lon: 2.1356 },
  'gravelines': { lat: 51.01666, lon: 2.1356 },
  'centrale de gravelines': { lat: 51.01666, lon: 2.1356 },
};

// Fonction pour normaliser le nom du site
function normalizeSiteName(name: string): string {
  return name.toLowerCase().trim();
}

// Exécuteur des outils
export async function executeTool(toolName: string, args: any): Promise<any> {
  try {
    switch (toolName) {
      case 'getCoordonnees': {
        const input = getCoordonneesSchema.parse(args);
        const normalizedName = normalizeSiteName(input.site_name);
        const coords = sitesDatabase[normalizedName];
        
        if (!coords) {
          throw new Error(`Site "${input.site_name}" non trouvé dans la base de données`);
        }
        
        return { lat: coords.lat, lon: coords.lon };
      }

      case 'getEtatInitial': {
        getEtatInitialSchema.parse(args);
        // Valeurs par défaut
        return {
          home: { lat: 48.8566, lon: 2.3522, alt: 0 },
          cruise_alt: 50,
          speed: 5,
        };
      }

      case 'getZoneInterdite': {
        getZoneInterditeSchema.parse(args);
        // Retourne un tableau vide pour l'instant
        return [];
      }

      case 'planMissionRecon': {
        const input = planMissionReconSchema.parse(args);
        // Génère 3 waypoints en orbite autour de la cible
        const waypoints = [];
        for (let i = 0; i < 3; i++) {
          const angle = (i * 2 * Math.PI) / 3;
          const lat = input.lat + (input.radius_m / 111000) * Math.cos(angle);
          const lon = input.lon + (input.radius_m / 111000) * Math.sin(angle) / Math.cos(input.lat * Math.PI / 180);
          waypoints.push({ lat, lon, alt: input.alt_m });
        }
        return { waypoints };
      }

      case 'takeOff': {
        const input = takeOffSchema.parse(args);
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'takeoff',
          parameters: input.alt_m ? { alt_m: input.alt_m } : {},
        });
        return response.data;
      }

      case 'goTo': {
        const input = goToSchema.parse(args);
        const parameters: any = {
          lat: input.lat,
          lon: input.lon,
          alt_m: input.alt_m,
        };
        if (input.speed_mps !== undefined) {
          parameters.speed_mps = input.speed_mps;
        }
        if (input.orientation_mode !== undefined) {
          parameters.orientation_mode = input.orientation_mode;
        }
        if (input.heading !== undefined) {
          parameters.heading = input.heading;
        }
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'goto',
          parameters: parameters,
        });
        return response.data;
      }

      case 'circle': {
        const input = circleSchema.parse(args);
        const parameters: any = {
          target_lat: input.target_lat,
          target_lon: input.target_lon,
          alt_m: input.alt_m,
          radius_m: input.radius_m,
        };
        if (input.laps !== undefined) {
          parameters.laps = input.laps;
        }
        if (input.direction !== undefined) {
          parameters.direction = input.direction;
        }
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'circle',
          parameters: parameters,
        });
        return response.data;
      }

      case 'capture': {
        const input = captureSchema.parse(args);
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'capture',
          parameters: {
            type: input.type,
            duration_s: input.duration_s,
          },
        });
        return response.data;
      }

      case 'returnToHome': {
        returnToHomeSchema.parse(args);
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'rth',
          parameters: {},
        });
        return response.data;
      }

      case 'land': {
        landSchema.parse(args);
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'land',
          parameters: {},
        });
        return response.data;
      }

      case 'getStatus': {
        getStatusSchema.parse(args);
        const response = await axios.post(`${DRONE_API_URL}/cmd`, {
          id: `cmd_${Date.now()}`,
          action: 'status',
          parameters: {},
        });
        return response.data;
      }

      default:
        throw new Error(`Outil inconnu: ${toolName}`);
    }
  } catch (error: any) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Erreur lors de l'exécution de ${toolName}: ${error.message || 'Erreur inconnue'}`);
  }
}

