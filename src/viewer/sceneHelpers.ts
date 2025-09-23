import * as BABYLON from '@babylonjs/core'

/**
 * Rename __root__ nodes to include the model filename for clarity
 * @param meshes - Array of meshes from the loaded model
 * @param transformNodes - Array of transform nodes from the loaded model
 * @param filename - The original filename of the model
 */
export function renameRootNodes(
    meshes: BABYLON.AbstractMesh[],
    transformNodes: BABYLON.TransformNode[] | undefined,
    filename: string
): void {
    // Get the base name of the file (without extension)
    const modelName = filename.substring(0, filename.lastIndexOf('.')) || filename

    // Rename __root__ meshes
    meshes.forEach(mesh => {
        if (mesh.name === '__root__') {
            mesh.name = `${modelName}_root`
        }
    })

    // Rename __root__ transform nodes
    transformNodes?.forEach(node => {
        if (node.name === '__root__') {
            node.name = `${modelName}_root`
        }
    })
}