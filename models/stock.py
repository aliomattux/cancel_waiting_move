from openerp import api
from openerp.osv import osv, fields

class StockPicking(osv.osv):
    _inherit = 'stock.picking'

    def picking_cancel_waiting_moves(self, cr, uid, ids, context=None):
	move_obj = self.pool.get('stock.move')
        for picking in self.browse(cr, uid, ids):
            move_obj.cancel_waiting_moves(cr, uid, False, picking.move_lines, context=context)

        return True


class StockMove(osv.osv):
    _inherit = 'stock.move'


    def button_cancel_waiting_moves(self, cr, uid, ids, context=None):
        return self.cancel_waiting_moves(cr, uid, ids, False, context=context)


    def cancel_waiting_moves(self, cr, uid, ids, moves=False, context=None):
	picking_obj = self.pool.get('stock.picking')
	#This should only be run from a single picking
	#Done so browse object can be used at end
	if not moves:
	    moves = self.browse(cr, uid, ids)

	for move in moves:
	    if move.state == 'waiting':
		#Ancestors are moves that when complete will make this move available
		#Since we want to cancel this operation and allocate elsewhere
		#We want to make sure we remove the reference on the ancestor moves
		ancestors = self.find_move_ancestors(cr, uid, move, context=context)
		if ancestors:
		    self.write(cr, uid, ancestors, {'move_dest_id': False}, context=context)

	        #Reset the state of the move
	        self.write(cr, uid, [move.id], {'state': 'confirmed'}, context=context)

	#The reason I do to the picking instead of move is because I want to ensure
	#If that the picking state is changed if applicable. action_assign in stock.move
	#Does nothing to update the picking itself
	picking_obj.action_assign(cr, uid, [moves[0].picking_id.id])

	return True

