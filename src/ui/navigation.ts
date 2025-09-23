export class Navigation {
    private sidebar: HTMLElement | null = null;
    private isSidebarVisible: boolean = true;

    constructor() {
        this.initializeNavigation();
        this.setupEventListeners();
    }

    private initializeNavigation(): void {
        this.sidebar = document.getElementById('sidebar');

        // Add IDs to sidebar if not present
        if (this.sidebar && !this.sidebar.id) {
            this.sidebar.id = 'sidebar';
        }
    }

    private setupEventListeners(): void {
        // Navigation control buttons from navbar
        this.setupNavButton('navResetView', () => {
            const resetBtn = document.getElementById('resetView');
            if (resetBtn) resetBtn.click();
        });

        this.setupNavButton('navToggleGrid', () => {
            const gridBtn = document.getElementById('toggleGrid');
            if (gridBtn) gridBtn.click();
        });

        this.setupNavButton('navToggleSkybox', () => {
            const skyboxBtn = document.getElementById('toggleSkybox');
            if (skyboxBtn) skyboxBtn.click();
        });

        this.setupNavButton('navToggleSidebar', () => {
            this.toggleSidebar();
        });

        // Fit to view button
        this.setupNavButton('fitToView', () => {
            this.fitModelToView();
        });

        // Wireframe toggle button
        this.setupNavButton('toggleWireframe', () => {
            this.toggleWireframeMode();
        });

        // User menu dropdown
        this.setupUserDropdown();
    }

    private setupNavButton(id: string, handler: () => void): void {
        const button = document.getElementById(id);
        if (button) {
            button.addEventListener('click', handler);
        }
    }

    private toggleSidebar(): void {
        if (this.sidebar) {
            this.isSidebarVisible = !this.isSidebarVisible;
            this.sidebar.classList.toggle('sidebar-hidden', !this.isSidebarVisible);

            // Adjust viewer container width
            const viewerContainer = document.querySelector('.viewer-container') as HTMLElement;
            if (viewerContainer) {
                viewerContainer.classList.toggle('full-width', !this.isSidebarVisible);
            }
        }
    }

    private fitModelToView(): void {
        // This will be implemented to fit the current model in view
        // For now, trigger reset view
        const event = new CustomEvent('fitToView');
        window.dispatchEvent(event);
    }

    private toggleWireframeMode(): void {
        // Dispatch custom event for wireframe toggle
        const event = new CustomEvent('toggleWireframe');
        window.dispatchEvent(event);
    }

    private setupUserDropdown(): void {
        const userDropdown = document.querySelector('.user-dropdown');
        const dropdownMenu = document.querySelector('.user-dropdown-menu');

        if (userDropdown && dropdownMenu) {
            userDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('hidden');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdownMenu.classList.add('hidden');
            });
        }
    }

    public updateUserMenu(user: { name: string; email: string } | null): void {
        const authSection = document.getElementById('authSection');
        const userMenu = document.getElementById('userMenu');
        const username = document.getElementById('username');
        const userInitial = document.getElementById('userInitial');
        const loginBtn = document.getElementById('loginBtn');

        if (user) {
            // User is logged in
            if (authSection) authSection.classList.add('hidden');
            if (userMenu) userMenu.classList.remove('hidden');
            if (username) username.textContent = user.name;
            if (userInitial) userInitial.textContent = user.name.charAt(0).toUpperCase();
            if (loginBtn) loginBtn.classList.add('hidden');
        } else {
            // User is logged out
            if (authSection) authSection.classList.remove('hidden');
            if (userMenu) userMenu.classList.add('hidden');
            if (loginBtn) loginBtn.classList.remove('hidden');
        }
    }
}