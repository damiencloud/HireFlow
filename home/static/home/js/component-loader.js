/**
 * HireFlow Component Loader - App Modular Version (Recursive)
 * Asynchronously loads reusable HTML templates into placeholders using server-absolute paths.
 * Supports nesting components recursively.
 */

document.addEventListener("DOMContentLoaded", () => {
    loadComponents(document);
});

/**
 * Recursively scans a container element for [data-component] placeholders and loads their templates.
 * @param {HTMLElement|Document} container - The container element to scan.
 */
async function loadComponents(container = document) {
    const placeholders = container.querySelectorAll("[data-component]");
    
    for (const placeholder of placeholders) {
        const componentName = placeholder.getAttribute("data-component");
        if (!componentName) continue;
        
        // Remove the attribute immediately to prevent duplicate runs or circular dependencies
        placeholder.removeAttribute("data-component");
        
        // Use a root-relative (server-absolute) path
        const componentPath = `/home/templates/home/components/${componentName}.html`;
        
        try {
            const response = await fetch(componentPath);
            if (!response.ok) {
                throw new Error(`Failed to fetch component: ${componentName} (Status: ${response.status})`);
            }
            
            const htmlContent = await response.text();
            placeholder.innerHTML = htmlContent;
            
            // RECURSIVE STEP: Scan the newly injected content for nested component placeholders
            await loadComponents(placeholder);
            
            // Dispatch custom load event
            const event = new CustomEvent("componentLoaded", { detail: { name: componentName } });
            document.dispatchEvent(event);
            
        } catch (error) {
            console.error(`[HireFlow Loader Error]:`, error);
            placeholder.innerHTML = `
                <div class="alert alert-danger py-2 px-3 m-2 text-center" role="alert" style="font-size: 0.875rem;">
                    <strong>Error:</strong> Failed to load component: <code>${componentName}</code>. 
                    Ensure you are running this page on a local web server (HTTP) rather than opening the file directly (file://).
                </div>
            `;
        }
    }
}
