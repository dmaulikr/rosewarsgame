package com.wotr.model;

import com.wotr.model.unit.Unit;

public class Action {

	private final Position pos;
	private final ActionPath path;
	private final Unit unit;

	public Position getPosition() {
		return pos;
	}

	public Action(Unit unit, Position pos, ActionPath path) {
		this.unit = unit;
		this.pos = pos;
		this.path = path;
	}	

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((pos == null) ? 0 : pos.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Action other = (Action) obj;
		if (pos == null) {
			if (other.pos != null)
				return false;
		} else if (!pos.equals(other.pos))
			return false;
		return true;
	}

	public String toString() {
		return getClass().getSimpleName() + " at " + pos + ". Path = " + path;
	}

	public ActionPath getPath() {
		return path;
	}

	public Unit getUnit() {
		return unit;
	}
}
