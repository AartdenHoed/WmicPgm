using ConfigMan.ActionFilters;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace ConfigMan.Controllers
{
    [LogActionFilter]
    [HandleError]

    public class DocumentationsController : Controller
    {
        // GET: Documentations
        public ActionResult Index()
        {
            string controllerName = this.ControllerContext.RouteData.Values["controller"].ToString();
            ViewBag.SympaMsg = controllerName + " not implemented yet";
            return View("../Shared/Error");
        }
    }
}