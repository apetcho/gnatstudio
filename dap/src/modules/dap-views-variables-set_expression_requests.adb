------------------------------------------------------------------------------
--                               GNAT Studio                                --
--                                                                          --
--                     Copyright (C) 2023, AdaCore                          --
--                                                                          --
-- This is free software;  you can redistribute it  and/or modify it  under --
-- terms of the  GNU General Public License as published  by the Free Soft- --
-- ware  Foundation;  either version 3,  or (at your option) any later ver- --
-- sion.  This software is distributed in the hope  that it will be useful, --
-- but WITHOUT ANY WARRANTY;  without even the implied warranty of MERCHAN- --
-- TABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public --
-- License for  more details.  You should have  received  a copy of the GNU --
-- General  Public  License  distributed  with  this  software;   see  file --
-- COPYING3.  If not, go to http://www.gnu.org/licenses for a complete copy --
-- of the license.                                                          --
------------------------------------------------------------------------------

with VSS.Strings.Conversions;

with Glib_Values_Utils;           use Glib_Values_Utils;

with Gdk.RGBA;                    use Gdk.RGBA;

with GPS.Kernel.Preferences;      use GPS.Kernel.Preferences;

package body DAP.Views.Variables.Set_Expression_Requests is

   -----------------------
   -- On_Result_Message --
   -----------------------

   overriding procedure On_Result_Message
     (Self        : in out Set_Expression_Request;
      Result      : in out DAP.Tools.SetExpressionResponse;
      New_Request : in out DAP.Requests.DAP_Request_Access)
   is
      View : constant DAP_Variables_View :=
        Variables_MDI_Views.Retrieve_View
          (Self.Kernel,
           Visible_Only => False);

      Iter   : Gtk_Tree_Iter;
      Cursor : Variables_References_Trees.Cursor;
      Found  : Boolean;
      Var    : DAP.Tools.Variable;
   begin
      New_Request := null;

      if Result.success then
         if View /= null then
            Cursor := View.Locals.Root;
            Find_Best_Ref (Self.Name, Cursor, Found);
            if Found then
               Var := Element (Cursor);

               Var.a_type             := Result.a_body.a_type;
               Var.value              := Result.a_body.value;
               Var.indexedVariables   := Result.a_body.indexedVariables;
               Var.namedVariables     := Result.a_body.namedVariables;
               Var.presentationHint   := Result.a_body.presentationHint;
               Var.variablesReference :=
                 (if Result.a_body.variablesReference.Is_Set
                  then Result.a_body.variablesReference.Value
                  else 0);

               View.Locals.Replace_Element (Cursor, Var);
            end if;

            Iter := View.Tree.Model.Get_Iter (Self.Path);
            Set_And_Clear
              (View.Tree.Model,
               Iter    => Iter,
               Columns => (Column_Value, Column_Value_Fg),
               Values  =>
                 (1 => As_String
                      (VSS.Strings.Conversions.To_UTF_8_String
                           (Result.a_body.value)),
                  2 => As_String (To_String (Numbers_Style.Get_Pref_Fg))));
         end if;

      else
         Self.Kernel.Get_Messages_Window.Insert_Error
           (VSS.Strings.Conversions.To_UTF_8_String (Self.Name) &
              " is not set.");
      end if;

      Path_Free (Self.Path);
   end On_Result_Message;

end DAP.Views.Variables.Set_Expression_Requests;
