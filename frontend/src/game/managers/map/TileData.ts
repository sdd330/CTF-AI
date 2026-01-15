/**
 * TileData - 图块数据（享元模式）
 */
/**
 * 图块数据（享元模式）
 */
export class TileData {
  private static cache: Map<number, TileData> = new Map()
  
  constructor(
    public readonly tileId: number,
    public readonly isCollidable: boolean = false
  ) {}

  /**
   * 享元工厂方法
   */
  static getTileData(tileId: number, isCollidable: boolean = false): TileData {
    const key = tileId * 1000 + (isCollidable ? 1 : 0)
    if (!TileData.cache.has(key)) {
      TileData.cache.set(key, new TileData(tileId, isCollidable))
    }
    return TileData.cache.get(key)!
  }
}
