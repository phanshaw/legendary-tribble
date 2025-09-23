import * as BABYLON from '@babylonjs/core'
import { getScene } from '../viewer/scene'

interface TreeNode {
    mesh: BABYLON.AbstractMesh | BABYLON.TransformNode
    element: HTMLElement
    childrenContainer: HTMLElement | null
    expanded: boolean
    children: TreeNode[]
}

export class SceneView {
    private container: HTMLElement | null = null
    private treeContainer: HTMLElement | null = null
    private inspectorContainer: HTMLElement | null = null
    private selectedNode: BABYLON.AbstractMesh | BABYLON.TransformNode | null = null
    private nodeMap: Map<BABYLON.AbstractMesh | BABYLON.TransformNode, TreeNode> = new Map()
    private elementPool: HTMLElement[] = []
    private poolIndex: number = 0
    private updateTimer: number | null = null
    private isVisible: boolean = false
    private resizeDivider: HTMLElement | null = null
    private isResizing: boolean = false

    constructor() {
        this.createSceneView()
        this.setupEventListeners()
        this.startSceneMonitoring()
    }

    private createSceneView(): void {
        // Create main container
        this.container = document.createElement('div')
        this.container.className = 'scene-view-panel'
        this.container.innerHTML = `
            <div class="scene-view-header">
                <h3>Scene Hierarchy</h3>
                <button class="scene-view-close" title="Close">×</button>
            </div>
            <div class="scene-view-content">
                <div class="scene-tree-wrapper">
                    <div class="scene-tree-container" id="sceneTreeContainer"></div>
                </div>
                <div class="scene-resize-divider" id="sceneResizeDivider"></div>
                <div class="scene-inspector" id="sceneInspector">
                    <div class="inspector-header">Inspector</div>
                    <div class="inspector-content">
                        <p class="inspector-placeholder">Select an object to inspect</p>
                    </div>
                </div>
            </div>
        `

        document.body.appendChild(this.container)

        this.treeContainer = document.getElementById('sceneTreeContainer')
        this.inspectorContainer = this.container.querySelector('.inspector-content')
        this.resizeDivider = document.getElementById('sceneResizeDivider')

        // Set initial sizes (2/3 for tree, 1/3 for inspector)
        const treeWrapper = this.container.querySelector('.scene-tree-wrapper') as HTMLElement
        const inspector = document.getElementById('sceneInspector') as HTMLElement

        // Heights are set via CSS, no need to set them here

        // Initially hidden
        this.container.style.display = 'none'
    }

    private setupEventListeners(): void {
        // Close button
        const closeBtn = this.container?.querySelector('.scene-view-close')
        closeBtn?.addEventListener('click', () => this.toggle())

        // Setup resize divider
        this.setupResizeDivider()

        // Toggle scene view button (add to existing controls)
        const toggleBtn = document.createElement('button')
        toggleBtn.id = 'toggleSceneView'
        toggleBtn.className = 'control-btn'
        toggleBtn.title = 'Toggle Scene View'
        toggleBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="5"/>
                <rect x="3" y="12" width="18" height="9"/>
                <line x1="7" y1="16" x2="11" y2="16"/>
                <line x1="7" y1="18" x2="11" y2="18"/>
            </svg>
            Scene
        `

        // Add to viewer controls
        const viewerControls = document.querySelector('.viewer-controls')
        if (viewerControls) {
            viewerControls.appendChild(toggleBtn)
            toggleBtn.addEventListener('click', () => this.toggle())
        }

        // Scene selection
        const scene = getScene()
        if (scene) {
            scene.onPointerObservable.add((pointerInfo) => {
                if (pointerInfo.type === BABYLON.PointerEventTypes.POINTERPICK && pointerInfo.pickInfo?.hit) {
                    this.selectMesh(pointerInfo.pickInfo.pickedMesh)
                }
            })
        }
    }

    private setupResizeDivider(): void {
        if (!this.resizeDivider) return

        let startY = 0
        let startTreeHeight = 0
        let startInspectorHeight = 0
        let totalHeight = 0
        const treeWrapper = this.container?.querySelector('.scene-tree-wrapper') as HTMLElement
        const inspector = document.getElementById('sceneInspector') as HTMLElement

        const onMouseDown = (e: MouseEvent) => {
            e.preventDefault()
            this.isResizing = true
            startY = e.clientY

            // Get current heights
            const treeRect = treeWrapper?.getBoundingClientRect()
            const inspectorRect = inspector?.getBoundingClientRect()
            startTreeHeight = treeRect?.height || 0
            startInspectorHeight = inspectorRect?.height || 0

            // Calculate total available height
            const contentElement = treeWrapper?.parentElement as HTMLElement
            totalHeight = contentElement?.clientHeight || 0

            // Subtract divider height from total
            const dividerHeight = this.resizeDivider?.clientHeight || 4
            totalHeight = totalHeight - dividerHeight

            document.addEventListener('mousemove', onMouseMove)
            document.addEventListener('mouseup', onMouseUp)
            document.body.style.cursor = 'ns-resize'
            document.body.style.userSelect = 'none' // Prevent text selection during drag
            this.resizeDivider!.classList.add('resizing')
        }

        const onMouseMove = (e: MouseEvent) => {
            if (!this.isResizing) return

            e.preventDefault() // Prevent text selection during drag

            const deltaY = e.clientY - startY
            const minHeight = 100 // Minimum height for each panel
            const maxPanelHeight = totalHeight * 0.66 // Max 2/3 for any panel

            let newTreeHeight = startTreeHeight + deltaY
            let newInspectorHeight = totalHeight - newTreeHeight

            // Enforce minimum heights
            if (newTreeHeight < minHeight) {
                newTreeHeight = minHeight
                newInspectorHeight = totalHeight - minHeight
            }
            if (newInspectorHeight < minHeight) {
                newInspectorHeight = minHeight
                newTreeHeight = totalHeight - minHeight
            }

            // Enforce maximum height for tree (2/3 of total)
            if (newTreeHeight > maxPanelHeight) {
                newTreeHeight = maxPanelHeight
                newInspectorHeight = totalHeight - maxPanelHeight
            }

            // Enforce maximum height for inspector (2/3 of total)
            if (newInspectorHeight > maxPanelHeight) {
                newInspectorHeight = maxPanelHeight
                newTreeHeight = totalHeight - maxPanelHeight
            }

            // Apply heights directly and remove max-height to allow resize
            if (treeWrapper) {
                treeWrapper.style.flex = 'none'
                treeWrapper.style.height = `${newTreeHeight}px`
                treeWrapper.style.maxHeight = 'none' // Override CSS max-height during resize
            }
            if (inspector) {
                inspector.style.flex = 'none'
                inspector.style.height = `${newInspectorHeight}px`
            }
        }

        const onMouseUp = () => {
            this.isResizing = false
            document.removeEventListener('mousemove', onMouseMove)
            document.removeEventListener('mouseup', onMouseUp)
            document.body.style.cursor = ''
            document.body.style.userSelect = ''
            this.resizeDivider?.classList.remove('resizing')
        }

        this.resizeDivider.addEventListener('mousedown', onMouseDown)
    }

    private startSceneMonitoring(): void {
        // Monitor scene changes with debouncing
        setInterval(() => {
            if (this.isVisible) {
                if (this.updateTimer) {
                    clearTimeout(this.updateTimer)
                }
                this.updateTimer = window.setTimeout(() => {
                    this.refreshSceneTree()
                }, 100)
            }
        }, 500)
    }

    public toggle(): void {
        this.isVisible = !this.isVisible
        if (this.container) {
            this.container.style.display = this.isVisible ? 'block' : 'none'
            if (this.isVisible) {
                this.refreshSceneTree()
            }
        }

        // Update button state
        const btn = document.getElementById('toggleSceneView')
        if (btn) {
            btn.classList.toggle('active', this.isVisible)
        }
    }

    private refreshSceneTree(): void {
        const scene = getScene()
        if (!scene || !this.treeContainer) return

        // Reset pool
        this.poolIndex = 0
        this.nodeMap.clear()

        // Clear container
        this.treeContainer.innerHTML = ''

        // Get root nodes (meshes without parents or with non-mesh parents)
        const rootNodes = scene.meshes.filter(mesh => {
            // Include all root meshes, we'll handle system meshes differently in display
            return !mesh.parent || !(mesh.parent instanceof BABYLON.AbstractMesh || mesh.parent instanceof BABYLON.TransformNode)
        })

        // Also add transform nodes that are roots
        scene.transformNodes.forEach(node => {
            if (!node.parent || !(node.parent instanceof BABYLON.AbstractMesh || node.parent instanceof BABYLON.TransformNode)) {
                rootNodes.push(node as any)
            }
        })

        // Build tree for each root
        rootNodes.forEach(root => {
            const treeNode = this.createTreeNode(root, 0)
            if (treeNode) {
                this.treeContainer!.appendChild(treeNode.element)
            }
        })
    }

    private createTreeNode(node: BABYLON.AbstractMesh | BABYLON.TransformNode, depth: number): TreeNode | null {
        // Get or create element from pool
        const element = this.getPooledElement()

        const hasChildren = this.hasChildren(node)
        const isExpanded = true // Default expanded for now
        const isSystemMesh = this.isSystemMesh(node)

        // Create node structure
        element.className = `tree-node ${isSystemMesh ? 'system-mesh' : ''}`
        element.style.paddingLeft = `${depth * 20 + 5}px`
        element.innerHTML = `
            <div class="tree-node-content">
                ${hasChildren ? `<span class="tree-arrow ${isExpanded ? 'expanded' : ''}">▶</span>` : '<span class="tree-spacer"></span>'}
                <span class="tree-icon">${this.getNodeIcon(node)}</span>
                <span class="tree-label">${this.getDisplayName(node)}</span>
            </div>
        `

        const treeNode: TreeNode = {
            mesh: node,
            element,
            childrenContainer: null,
            expanded: isExpanded,
            children: []
        }

        // Store in map
        this.nodeMap.set(node, treeNode)

        // Setup click handlers (but not for system meshes)
        const content = element.querySelector('.tree-node-content') as HTMLElement
        if (!isSystemMesh) {
            content.addEventListener('click', (e) => {
                e.stopPropagation()
                this.selectMesh(node)
            })
        } else {
            content.style.cursor = 'default'
        }

        // Setup expand/collapse
        if (hasChildren) {
            const arrow = element.querySelector('.tree-arrow')
            arrow?.addEventListener('click', (e) => {
                e.stopPropagation()
                this.toggleExpand(treeNode)
            })

            // Create children container
            if (isExpanded) {
                treeNode.childrenContainer = document.createElement('div')
                treeNode.childrenContainer.className = 'tree-children'
                element.appendChild(treeNode.childrenContainer)

                // Add children
                this.addChildren(treeNode, depth + 1)
            }
        }

        return treeNode
    }

    private hasChildren(node: BABYLON.AbstractMesh | BABYLON.TransformNode): boolean {
        return node.getChildren().length > 0
    }

    private addChildren(parentNode: TreeNode, depth: number): void {
        if (!parentNode.childrenContainer) return

        const children = parentNode.mesh.getChildren()
        children.forEach(child => {
            if (child instanceof BABYLON.AbstractMesh || child instanceof BABYLON.TransformNode) {
                const childNode = this.createTreeNode(child, depth)
                if (childNode) {
                    parentNode.children.push(childNode)
                    parentNode.childrenContainer!.appendChild(childNode.element)
                }
            }
        })
    }

    private toggleExpand(node: TreeNode): void {
        node.expanded = !node.expanded
        const arrow = node.element.querySelector('.tree-arrow')

        if (node.expanded) {
            arrow?.classList.add('expanded')

            if (!node.childrenContainer) {
                node.childrenContainer = document.createElement('div')
                node.childrenContainer.className = 'tree-children'
                node.element.appendChild(node.childrenContainer)

                const depth = Math.floor((parseInt(node.element.style.paddingLeft) - 5) / 20) + 1
                this.addChildren(node, depth)
            } else {
                node.childrenContainer.style.display = 'block'
            }
        } else {
            arrow?.classList.remove('expanded')
            if (node.childrenContainer) {
                node.childrenContainer.style.display = 'none'
            }
        }
    }

    private getPooledElement(): HTMLElement {
        if (this.poolIndex < this.elementPool.length) {
            return this.elementPool[this.poolIndex++]
        }

        const element = document.createElement('div')
        this.elementPool.push(element)
        this.poolIndex++
        return element
    }

    private isSystemMesh(node: BABYLON.AbstractMesh | BABYLON.TransformNode): boolean {
        return node.name === 'ground' ||
               node.id === 'grid' ||
               node.name === 'skybox' ||
               node.name === 'BackgroundSkybox' ||
               node.name === 'BackgroundPlane'
    }

    private getDisplayName(node: BABYLON.AbstractMesh | BABYLON.TransformNode): string {
        // Special case for the model container - show as "Scene"
        if (node.name === 'modelContainer') {
            return 'Scene'
        }
        return node.name || 'Unnamed'
    }

    private getNodeIcon(node: BABYLON.AbstractMesh | BABYLON.TransformNode): string {
        if (this.isSystemMesh(node)) {
            if (node.id === 'grid' || node.name === 'ground') {
                return '⚡'  // Grid icon
            } else if (node.name === 'skybox' || node.name === 'BackgroundSkybox') {
                return '☁️'  // Sky icon
            }
            return '⚙️'  // System icon
        }

        // Check the actual class name for more accurate type detection
        const className = node.getClassName()

        if (className === 'Mesh') {
            // It's specifically a Mesh type
            return '⊞'  // Squared plus icon for meshes
        } else if (className === 'TransformNode') {
            // Special case for the model container
            if (node.name === 'modelContainer' || node.name === 'Scene') {
                return '🌐'  // Globe icon for scene container
            }
            // Use axis icon for transform nodes
            return '✣'  // Four balloon-spoked asterisk for transform/axis
        } else if (node instanceof BABYLON.AbstractMesh) {
            // Other mesh types (InstancedMesh, GroundMesh, etc.)
            if (node.name.toLowerCase().includes('camera')) {
                return '📷'
            } else if (node.name.toLowerCase().includes('light')) {
                return '💡'
            }
            // Default to squared plus for any mesh-like object
            return '⊞'
        }

        return '○'
    }

    private selectMesh(mesh: BABYLON.AbstractMesh | BABYLON.TransformNode | null): void {
        if (!mesh) return

        // Update selection state
        this.selectedNode = mesh

        // Update tree highlighting
        this.nodeMap.forEach((node, nodeMesh) => {
            if (nodeMesh === mesh) {
                node.element.classList.add('selected')
            } else {
                node.element.classList.remove('selected')
            }
        })

        // Update inspector
        this.updateInspector(mesh)

        // Highlight in scene
        const scene = getScene()
        if (scene) {
            // Clear previous highlights
            scene.meshes.forEach(m => {
                if (m.material && 'emissiveColor' in m.material) {
                    (m.material as any).emissiveColor = new BABYLON.Color3(0, 0, 0)
                }
            })

            // Highlight selected
            if (mesh instanceof BABYLON.AbstractMesh && mesh.material && 'emissiveColor' in mesh.material) {
                (mesh.material as any).emissiveColor = new BABYLON.Color3(0.1, 0.3, 0.5)
            }
        }
    }

    private updateInspector(node: BABYLON.AbstractMesh | BABYLON.TransformNode): void {
        if (!this.inspectorContainer) return

        const pos = node.position
        const rot = node.rotation
        const scale = node.scaling

        this.inspectorContainer.innerHTML = `
            <div class="inspector-section">
                <h4>${this.getNodeIcon(node)} ${this.getDisplayName(node)}</h4>
                <div class="inspector-property">
                    <label>Type:</label>
                    <span>${node.getClassName()}</span>
                </div>
                <div class="inspector-property">
                    <label>ID:</label>
                    <span>${node.id}</span>
                </div>
            </div>

            <div class="inspector-section">
                <h5>Transform</h5>
                <div class="inspector-property">
                    <label>Position:</label>
                    <span>X: ${pos.x.toFixed(2)}, Y: ${pos.y.toFixed(2)}, Z: ${pos.z.toFixed(2)}</span>
                </div>
                <div class="inspector-property">
                    <label>Rotation:</label>
                    <span>X: ${rot.x.toFixed(2)}, Y: ${rot.y.toFixed(2)}, Z: ${rot.z.toFixed(2)}</span>
                </div>
                <div class="inspector-property">
                    <label>Scale:</label>
                    <span>X: ${scale.x.toFixed(2)}, Y: ${scale.y.toFixed(2)}, Z: ${scale.z.toFixed(2)}</span>
                </div>
            </div>

            ${node instanceof BABYLON.AbstractMesh ? `
                <div class="inspector-section">
                    <h5>Mesh Info</h5>
                    <div class="inspector-property">
                        <label>Vertices:</label>
                        <span>${node.getTotalVertices()}</span>
                    </div>
                    <div class="inspector-property">
                        <label>Faces:</label>
                        <span>${node.getTotalIndices() / 3}</span>
                    </div>
                    <div class="inspector-property">
                        <label>Material:</label>
                        <span>${node.material?.name || 'None'}</span>
                    </div>
                </div>
            ` : ''}

            <div class="inspector-section">
                <h5>Hierarchy</h5>
                <div class="inspector-property">
                    <label>Parent:</label>
                    <span>${node.parent?.name || 'None'}</span>
                </div>
                <div class="inspector-property">
                    <label>Children:</label>
                    <span>${node.getChildren().length}</span>
                </div>
            </div>
        `
    }
}