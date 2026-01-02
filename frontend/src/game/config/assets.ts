export interface AssetConfig {
  key: string
  args: unknown[]
}

export interface AssetsConfig {
  image?: Record<string, AssetConfig>
  spritesheet?: Record<string, AssetConfig>
  tilemapTiledJSON?: Record<string, AssetConfig>
}

const ASSETS: AssetsConfig = {
  image: {
    red_flag_img: {
      key: 'red_flag_img',
      args: ['assets/red_flag_32_32.png']
    },
    yellow_flag_img: {
      key: 'yellow_flag_img',
      args: ['assets/yellow_flag_32_32.png']
    }
  },
  spritesheet: {
    tiles: {
      key: 'tiles',
      args: ['assets/tiles.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    },
    characters: {
      key: 'characters',
      args: ['assets/characters.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    },
    characters_L_flag: {
      key: 'characters_L_flag',
      args: ['assets/characters_yellow_flag.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    },
    characters_R_flag: {
      key: 'characters_R_flag',
      args: ['assets/characters_red_flag.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    },
    L_flag: {
      key: 'L_flag',
      args: ['assets/red_flag_32_32.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    },
    R_flag: {
      key: 'R_flag',
      args: ['assets/yellow_flag_32_32.png', {
        frameWidth: 32,
        frameHeight: 32
      }]
    }
  },
  tilemapTiledJSON: {
    map: {
      key: 'map',
      args: ['assets/tilemap.json']
    }
  }
}

export default ASSETS

